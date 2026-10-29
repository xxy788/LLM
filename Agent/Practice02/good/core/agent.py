"""Agent 核心：维护对话历史，与 LLM 流式交互并执行工具调用。

通过事件生成器（core.events.Event）与前端通信，不依赖任何输入/输出
设施（print/input），因此可同时被 TUI、Web、Desktop、Mobile 等前端复用。
"""

import json

import requests

from .config import load_llm_config
from .events import TextDelta, ToolCall
from .tools import tools, run_tool


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
                result = run_tool(name, call["function"]["arguments"])
                yield ToolCall(name, result)
                self.messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
