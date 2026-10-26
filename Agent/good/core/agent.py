"""Agent 核心：维护对话历史，与 LLM 流式交互并执行工具调用。

通过事件生成器（core.events.Event）与前端通信，不依赖任何输入/输出
设施（print/input），因此可同时被 TUI、Web、Desktop、Mobile 等前端复用。
"""

import json

import requests

from .config import load_llm_config
from .events import ConfirmationRequest, ErrorEvent, TextDelta, ToolCall
from . import cli
from .tools import tools, run_tool


def _format_http_error(response):
    """把非 200 响应转成可读的错误信息，优先取 API 返回的 error.message。"""
    detail = response.text[:500]
    try:
        detail = json.loads(response.text)["error"]["message"]
    except (ValueError, KeyError, TypeError):
        pass
    return f"请求失败（HTTP {response.status_code}）：{detail}"


class Agent:
    def __init__(self, base_url, api_key, model):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.messages = []

    @classmethod
    def from_config(cls, path=None):
        return cls(**load_llm_config(path))

    def _request_stream(self):
        return requests.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": self.messages,
                "tools": tools,
                "stream": True,
            },
            stream=True,
        )

    def chat(self, prompt):
        """发送一轮用户输入，产生 Event 直到本轮对话（含工具调用）结束。"""
        self.messages.append({"role": "user", "content": prompt})
        while True:
            r = self._request_stream()
            if r.status_code != 200:
                yield ErrorEvent(_format_http_error(r))
                return
            reply = ""
            calls = {}
            for line in r.iter_lines():
                if line.startswith(b"data: ") and line != b"data: [DONE]":
                    delta = json.loads(line[6:])["choices"][0].get("delta", {})
                    text = delta.get("content") or ""
                    if text:
                        reply += text
                        yield TextDelta(text)
                    for tc in delta.get("tool_calls") or []:
                        call = calls.setdefault(
                            tc.get("index", 0),
                            {"id": "", "type": "function", "function": {"name": "", "arguments": ""}},
                        )
                        if tc.get("id"):
                            call["id"] = tc["id"]
                        f = tc.get("function") or {}
                        call["function"]["name"] += f.get("name") or ""
                        call["function"]["arguments"] += f.get("arguments") or ""

            call_list = [calls[i] for i in sorted(calls)]
            if not call_list:
                self.messages.append({"role": "assistant", "content": reply})
                return

            self.messages.append({"role": "assistant", "content": reply, "tool_calls": call_list})
            for call in call_list:
                name = call["function"]["name"]
                arguments = call["function"]["arguments"]
                if name == "RunCli":
                    command, args, error = cli.parse_cli_call(arguments)
                    if error:
                        result = error
                    else:
                        confirmation = ConfirmationRequest(command, args)
                        yield confirmation
                        if confirmation.wait():
                            result = run_tool(name, arguments, cli_approved=True)
                        else:
                            result = "错误：用户拒绝或未确认执行命令，命令未运行"
                else:
                    result = run_tool(name, arguments)
                yield ToolCall(name, result)
                self.messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
