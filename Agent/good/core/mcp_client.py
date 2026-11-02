"""MCP client connections and Function Calling tool adapters."""

import asyncio
import hashlib
import json
import os
import re
import threading
from contextlib import AsyncExitStack
from pathlib import Path


def find_mcp_config(path=None):
    """Find .mcp.json in the current project directory or one of its parents."""
    if path is not None:
        return Path(path).resolve()
    for directory in (Path.cwd(), *Path.cwd().parents):
        candidate = directory / ".mcp.json"
        if candidate.is_file():
            return candidate
    return None


def load_mcp_servers(path=None):
    """Load standard mcpServers configuration and return servers plus errors."""
    config_path = find_mcp_config(path)
    if config_path is None:
        return {}, []
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {}, [f"无法读取 MCP 配置 {config_path}: {error}"]
    servers = config.get("mcpServers") if isinstance(config, dict) else None
    if not isinstance(servers, dict):
        return {}, [f"MCP 配置 {config_path} 缺少有效的 mcpServers 对象"]
    return servers, []


def make_tool_schema(server_name, tool, reserved_names=()):
    """Convert an MCP tool to a uniquely named OpenAI Function Calling tool."""
    def field(name, *aliases):
        names = (name, *aliases)
        if isinstance(tool, dict):
            return next((tool[key] for key in names if key in tool), None)
        return next((getattr(tool, key) for key in names if hasattr(tool, key)), None)

    original_name = field("name")
    description = field("description")
    input_schema = field("inputSchema", "input_schema")
    raw_name = re.sub(r"[^a-zA-Z0-9_]", "_", f"mcp_{server_name}_{original_name}")
    name = raw_name[:64]
    if name in reserved_names:
        suffix = hashlib.sha1(f"{server_name}:{original_name}".encode()).hexdigest()[:8]
        name = f"{raw_name[:55]}_{suffix}"
    schema = input_schema if isinstance(input_schema, dict) else {}
    if schema.get("type") != "object":
        schema = {"type": "object", **schema}
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description or f"MCP 工具 {server_name}/{original_name}",
            "parameters": schema,
        },
    }


def format_call_result(result):
    """Preserve MCP text, structured, and non-text content in a model-safe string."""
    text_parts = []
    other_content = []
    for item in getattr(result, "content", None) or []:
        text = getattr(item, "text", None)
        if isinstance(text, str):
            text_parts.append(text)
        else:
            dump = getattr(item, "model_dump", None)
            other_content.append(dump(mode="json") if dump else str(item))

    structured = getattr(result, "structuredContent", None)
    if structured is None:
        structured = getattr(result, "structured_content", None)

    if structured is not None:
        output = {"structuredContent": structured}
        if text_parts:
            output["text"] = "\n".join(text_parts)
        if other_content:
            output["content"] = other_content
        content = json.dumps(output, ensure_ascii=False, default=str)
    elif text_parts and not other_content:
        content = "\n".join(text_parts)
    else:
        output = {"text": "\n".join(text_parts)} if text_parts else {}
        if other_content:
            output["content"] = other_content
        content = json.dumps(output, ensure_ascii=False, default=str)

    if getattr(result, "isError", False) or getattr(result, "is_error", False):
        return f"MCP 工具返回错误：{content}"
    return content


class MCPClientManager:
    """Keep SDK sessions alive on a private asyncio loop for the synchronous Agent."""

    def __init__(self, config_path=None, reserved_names=(), connect_timeout=15):
        self.errors = []
        self.tools = []
        self.tool_map = {}
        self._queues = {}
        self._workers = {}
        self._loop = None
        self._thread = None
        self._closed = False
        self._config_path = find_mcp_config(config_path)
        servers, errors = load_mcp_servers(self._config_path)
        self.errors.extend((None, error) for error in errors)
        if not servers:
            return

        self._servers = servers
        self._reserved_names = set(reserved_names)
        self._connect_timeout = connect_timeout
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        future = asyncio.run_coroutine_threadsafe(self._connect_all(), self._loop)
        try:
            future.result(timeout=connect_timeout * 2 * max(1, len(servers)) + 2)
        except Exception as error:
            self.errors.append((None, f"MCP 初始化失败：{type(error).__name__}: {error}"))

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _connect_all(self):
        results = await asyncio.gather(
            *(self._connect_one(name, config) for name, config in self._servers.items()),
            return_exceptions=True,
        )
        for server_name, result in zip(self._servers, results):
            if isinstance(result, BaseException):
                self.errors.append(
                    (server_name, f"MCP Server '{server_name}' 连接失败：{type(result).__name__}: {result}")
                )

    async def _connect_one(self, server_name, config):
        queue = asyncio.Queue()
        ready = self._loop.create_future()
        worker = asyncio.create_task(self._server_worker(server_name, config, queue, ready))
        try:
            discovered_tools = await asyncio.wait_for(
                asyncio.shield(ready), timeout=self._connect_timeout * 2
            )
        except asyncio.TimeoutError:
            worker.cancel()
            await asyncio.gather(worker, return_exceptions=True)
            self.errors.append(
                (server_name, f"MCP Server '{server_name}' 连接或发现工具超时")
            )
        except Exception as error:
            await asyncio.gather(worker, return_exceptions=True)
            self.errors.append(
                (server_name, f"MCP Server '{server_name}' 连接或发现工具失败：{type(error).__name__}: {error}")
            )
        else:
            self._queues[server_name] = queue
            self._workers[server_name] = worker
            for tool in discovered_tools:
                schema = make_tool_schema(
                    server_name,
                    tool,
                    self._reserved_names | set(self.tool_map),
                )
                exposed_name = schema["function"]["name"]
                self.tools.append(schema)
                self.tool_map[exposed_name] = (server_name, tool.name)

    async def _server_worker(self, server_name, config, queue, ready):
        try:
            async with AsyncExitStack() as stack:
                if not isinstance(config, dict):
                    raise ValueError("服务器配置必须是对象")
                transport = config.get("type")
                if transport == "stdio" or (transport is None and config.get("command")):
                    from mcp import StdioServerParameters
                    from mcp.client.stdio import stdio_client

                    command = config.get("command")
                    args = config.get("args", [])
                    if not isinstance(command, str) or not command:
                        raise ValueError("stdio 配置必须提供 command")
                    if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
                        raise ValueError("stdio args 必须是字符串数组")
                    env = config.get("env")
                    if env is not None and not isinstance(env, dict):
                        raise ValueError("stdio env 必须是对象")
                    process_env = os.environ.copy()
                    process_env.update(env or {})
                    cwd = config.get("cwd")
                    if cwd:
                        cwd_path = Path(cwd)
                        if not cwd_path.is_absolute():
                            cwd_path = self._config_path.parent / cwd_path
                        cwd = str(cwd_path.resolve())
                    parameters = StdioServerParameters(
                        command=command, args=args, env=process_env, cwd=cwd
                    )
                    read_stream, write_stream = await stack.enter_async_context(
                        stdio_client(parameters)
                    )
                elif transport in (None, "http", "streamable-http", "streamable_http"):
                    from mcp.client.streamable_http import (
                        create_mcp_http_client,
                        streamable_http_client,
                    )

                    url = config.get("url")
                    if not isinstance(url, str) or not url:
                        raise ValueError("Streamable HTTP 配置必须提供 url")
                    headers = config.get("headers", {})
                    if not isinstance(headers, dict) or not all(
                        isinstance(key, str) and isinstance(value, str)
                        for key, value in headers.items()
                    ):
                        raise ValueError("HTTP headers 必须是字符串键值对象")
                    http_client = create_mcp_http_client(headers=headers)
                    await stack.enter_async_context(http_client)
                    read_stream, write_stream = await stack.enter_async_context(
                        streamable_http_client(url, http_client=http_client)
                    )
                else:
                    raise ValueError(f"不支持的 MCP 传输方式：{transport}")

                from mcp import ClientSession

                session = await stack.enter_async_context(
                    ClientSession(read_stream, write_stream)
                )
                await asyncio.wait_for(session.initialize(), timeout=self._connect_timeout)
                result = await asyncio.wait_for(session.list_tools(), timeout=self._connect_timeout)
                if not ready.done():
                    ready.set_result(result.tools)

                while True:
                    request = await queue.get()
                    if request is None:
                        return
                    tool_name, arguments, response = request
                    try:
                        result = await session.call_tool(tool_name, arguments=arguments)
                        value = format_call_result(result)
                    except Exception as error:
                        value = f"MCP 工具 {tool_name} 调用失败：{type(error).__name__}: {error}"
                    if not response.done():
                        response.set_result(value)
        except asyncio.CancelledError:
            if not ready.done():
                ready.cancel()
            raise
        except Exception as error:
            if not ready.done():
                ready.set_exception(error)
            else:
                self.errors.append(
                    (server_name, f"MCP Server '{server_name}' 连接中断：{type(error).__name__}: {error}")
                )
        finally:
            while not queue.empty():
                request = queue.get_nowait()
                if request is not None:
                    _, _, response = request
                    if not response.done():
                        response.set_result(f"MCP Server '{server_name}' 已断开连接")

    def is_tool(self, name):
        return name in self.tool_map

    def call_tool(self, exposed_name, arguments):
        mapping = self.tool_map.get(exposed_name)
        if mapping is None:
            return f"错误：未找到 MCP 工具 {exposed_name}"
        if self._closed or self._loop is None:
            return f"错误：MCP 客户端已关闭，无法调用 {exposed_name}"
        server_name, tool_name = mapping
        future = asyncio.run_coroutine_threadsafe(
            self._call_tool(server_name, tool_name, arguments), self._loop
        )
        try:
            return future.result(timeout=60)
        except Exception as error:
            return f"MCP 工具 {exposed_name} 调用失败：{type(error).__name__}: {error}"

    async def _call_tool(self, server_name, tool_name, arguments):
        queue = self._queues.get(server_name)
        worker = self._workers.get(server_name)
        if queue is None or worker is None or worker.done():
            return f"错误：MCP Server '{server_name}' 当前不可用"
        response = self._loop.create_future()
        await queue.put((tool_name, arguments, response))
        return await response

    async def _close_sessions(self):
        for queue in self._queues.values():
            queue.put_nowait(None)
        if self._workers:
            await asyncio.gather(*self._workers.values(), return_exceptions=True)
        self._queues.clear()
        self._workers.clear()

    def close(self):
        if self._closed:
            return
        self._closed = True
        if self._loop is None:
            return
        future = asyncio.run_coroutine_threadsafe(self._close_sessions(), self._loop)
        try:
            future.result(timeout=10)
        except Exception:
            pass
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=10)