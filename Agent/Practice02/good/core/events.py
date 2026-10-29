"""核心层向前端发布的事件定义。

所有前端（tui / web / desktop / mobile …）统一消费这些事件，
前端只需识别事件类型即可渲染，无需了解 LLM 协议细节。
"""

from dataclasses import dataclass
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


Event = Union[TextDelta, ToolCall]
