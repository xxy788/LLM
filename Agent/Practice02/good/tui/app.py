"""Textual TUI 前端：以聊天形式与 Agent 交互。

职责仅限于：收集用户输入、渲染 core.events 事件流。
所有业务逻辑（对话历史、工具调用、LLM 通信）均在 core 层。
"""

import os

from textual import work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Input, Static

from core.agent import Agent
from core.events import TextDelta, ToolCall


class Message(Static):
    """一条聊天消息。role 决定样式：user / assistant / tool / hint。"""

    def __init__(self, text="", role="assistant"):
        # markup=False：工具结果中的 "[目录]" 等文本不能被当作 Rich 标记解析
        super().__init__(text, markup=False, classes=role)
        self.role = role


class AgentApp(App):
    TITLE = "FileTools Agent"
    CSS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.tcss")

    def __init__(self, agent: Agent):
        super().__init__()
        self.agent = agent
        self._busy = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(id="chat")
        yield Input(placeholder="输入你的问题，回车发送…", id="prompt")
        yield Footer()

    def on_mount(self):
        self.query_one("#prompt", Input).focus()
        self._add_message("你好，我是文件助手，有什么可以帮你？", "hint")

    def on_input_submitted(self, event: Input.Submitted):
        prompt = event.value.strip()
        event.input.clear()
        if not prompt:
            return
        if self._busy:
            self._add_message("上一条回复进行中，请稍候…", "hint")
            return
        self._add_message(f"你：{prompt}", "user")
        self._busy = True
        self._stream_reply(prompt)

    def _add_message(self, text: str, role: str) -> Message:
        chat = self.query_one("#chat", VerticalScroll)
        msg = Message(text, role)
        chat.mount(msg)
        chat.scroll_end(animate=False)
        return msg

    @work(thread=True)
    def _stream_reply(self, prompt: str):
        """在线程中消费 core 的事件流，通过 call_from_thread 回到 UI 线程渲染。"""
        try:
            current = None
            buffer = ""
            for event in self.agent.chat(prompt):
                if isinstance(event, TextDelta):
                    if current is None:
                        current = self.call_from_thread(self._add_message, "", "assistant")
                        buffer = ""
                    buffer += event.content
                    self.call_from_thread(current.update, buffer)
                elif isinstance(event, ToolCall):
                    current = None
                    buffer = ""
                    self.call_from_thread(
                        self._add_message, f"[tool {event.name}] {event.result}", "tool"
                    )
        except Exception as e:
            self.call_from_thread(self._add_message, f"错误：{e}", "hint")
        finally:
            self._busy = False
            chat = self.query_one("#chat", VerticalScroll)
            self.call_from_thread(chat.scroll_end, animate=False)
