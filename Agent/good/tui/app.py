"""Textual TUI 前端。

只做"事件 → 界面"的渲染：消费 core.agent.Agent 产生的
core.events 事件（TextDelta / ToolCall），不包含任何业务逻辑。
未来 web / desktop / mobile 前端按同样方式消费事件即可
（例如 TextDelta → SSE 推送，ToolCall → 结果面板）。
"""

from rich.markdown import Markdown

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Input, Static
from textual.screen import ModalScreen
from textual.widgets import Button

from core.agent import Agent
from core.events import ConfirmationRequest, ErrorEvent, TextDelta, ToolCall


class ConfirmCliScreen(ModalScreen[bool]):
    """Require an explicit per-command decision before local execution."""

    BINDINGS = [("escape", "reject", "拒绝")]

    CSS = """
    ConfirmCliScreen {
        align: center middle;
    }
    #confirm-dialog {
        width: 80%;
        max-width: 90;
        height: auto;
        max-height: 80%;
        border: round $warning;
        background: $surface;
        padding: 1 2;
    }
    #confirm-command {
        height: auto;
        max-height: 1fr;
        overflow-y: auto;
    }
    #confirm-buttons {
        height: 3;
        align-horizontal: right;
    }
    """

    def __init__(self, command: str, args: list[str]) -> None:
        super().__init__()
        import json

        self.command_text = json.dumps([command, *args], ensure_ascii=False, indent=2)

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Static("Agent 请求运行以下本地命令：", markup=False)
            yield Static(self.command_text, id="confirm-command", markup=False)
            with Horizontal(id="confirm-buttons"):
                yield Button("拒绝", id="reject")
                yield Button("执行", id="approve", variant="warning")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "approve":
            self.dismiss(True)
        elif event.button.id == "reject":
            self.dismiss(False)

    def action_reject(self) -> None:
        self.dismiss(False)


class FileAgentTUI(App[None]):
    """文件助手 Agent 的终端界面。"""

    TITLE = "文件助手 Agent"
    BINDINGS = [("ctrl+q", "quit", "退出")]

    CSS = """
    #chat {
        padding: 0 1;
    }
    #chat > Static {
        margin-bottom: 1;
        width: 100%;
    }
    .user {
        border: round $primary;
        border-title-color: $primary;
    }
    .assistant {
        border: round $success;
        border-title-color: $success;
    }
    .tool {
        border: round $warning;
        border-title-color: $warning;
        background: $surface;
    }
    .error {
        border: round $error;
        border-title-color: $error;
    }
    """

    def __init__(self, agent: Agent) -> None:
        super().__init__()
        self.agent = agent
        self._busy = False          # 一轮对话进行中，禁止并发提交
        self._reply_widget = None   # 当前正在流式输出的回复气泡
        self._reply_text = ""       # 已累积的回复文本

    # ---------- 布局 ----------

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with VerticalScroll(id="chat"):
            yield Static(
                "我是文件助手，可以查看、创建、编辑、删除文件和目录。",
                classes="assistant",
                markup=False,
            )
        yield Input(placeholder="请输入指令，回车发送…（Ctrl+Q 退出）")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#chat", VerticalScroll).scroll_end(animate=False)

    # ---------- 交互 ----------

    def on_input_submitted(self, event: Input.Submitted) -> None:
        prompt = event.value.strip()
        event.input.value = ""
        if not prompt or self._busy:
            return
        self._busy = True
        self._append_bubble(prompt, "user", "你")
        self._chat_worker(prompt)

    @work(thread=True, exclusive=True, group="chat")
    def _chat_worker(self, prompt: str) -> None:
        """在工作线程中驱动 Agent（阻塞式流式请求），事件投递回 UI 线程渲染。"""
        try:
            for ev in self.agent.chat(prompt):
                self.call_from_thread(self._render_event, ev)
            self.call_from_thread(self._finish_turn)
        except Exception as exc:  # 网络中断、协议异常等不能让界面卡死
            self.call_from_thread(self._render_error, f"{type(exc).__name__}: {exc}")

    # ---------- 渲染（均在 UI 线程执行） ----------

    def _append_bubble(self, text: str, cls: str, title: str) -> Static:
        chat = self.query_one("#chat", VerticalScroll)
        widget = Static(text, classes=cls, markup=False)
        widget.border_title = title
        chat.mount(widget)
        chat.scroll_end(animate=False)
        return widget

    def _render_event(self, ev) -> None:
        chat = self.query_one("#chat", VerticalScroll)
        if isinstance(ev, TextDelta):
            if self._reply_widget is None:
                self._reply_widget = self._append_bubble("", "assistant", "助手")
                self._reply_text = ""
            self._reply_text += ev.content
            self._reply_widget.update(self._reply_text)
            chat.scroll_end(animate=False)
        elif isinstance(ev, ToolCall):
            # 工具调用后的新回复另起一个气泡
            self._reply_widget = None
            self._reply_text = ""
            self._append_bubble(ev.result, "tool", f"工具: {ev.name}")
        elif isinstance(ev, ConfirmationRequest):
            self.push_screen(
                ConfirmCliScreen(ev.command, ev.args),
                lambda approved: ev.resolve(approved),
            )
        elif isinstance(ev, ErrorEvent):
            self._reply_widget = None
            self._reply_text = ""
            self._append_bubble(ev.message, "error", "错误")

    def _finish_turn(self) -> None:
        # 流式过程用纯文本，结束后整体替换为 Markdown 渲染
        if self._reply_widget is not None and self._reply_text.strip():
            self._reply_widget.update(Markdown(self._reply_text))
        self._reply_widget = None
        self._reply_text = ""
        self._busy = False

    def _render_error(self, message: str) -> None:
        self._append_bubble(message, "error", "错误")
        self._busy = False
