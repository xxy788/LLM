"""核心层向前端发布的事件定义。

所有前端（tui / web / desktop / mobile …）统一消费这些事件，
前端只需识别事件类型即可渲染，无需了解 LLM 协议细节。
"""

from dataclasses import dataclass, field
from threading import Event as ThreadEvent
from typing import Union


@dataclass
class TextDelta:
    """模型流式输出的文本片段。"""

    content: str


@dataclass
class ToolCall:
    """一次工具调用及其执行结果。"""

    name: str
    result: str


@dataclass
class ConfirmationRequest:
    """A local command awaiting an explicit user decision from the frontend."""

    command: str
    args: list
    _decision: ThreadEvent = field(default_factory=ThreadEvent, repr=False)
    approved: bool = False

    def resolve(self, approved):
        self.approved = bool(approved)
        self._decision.set()

    def wait(self, timeout=None):
        return self._decision.wait(timeout) and self.approved


@dataclass
class ErrorEvent:
    """请求或协议层错误，前端应以醒目方式提示用户。"""

    message: str


Event = Union[TextDelta, ToolCall, ConfirmationRequest, ErrorEvent]
