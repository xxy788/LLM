"""程序入口：组装 core 与前端并启动。

当前默认前端为 TUI（Textual）；未来新增 web / desktop / mobile 前端时，
只需新增对应前端目录并在此处（或各自的入口脚本中）替换前端实现，
core 层保持不变。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import Agent
from tui import AgentApp


def main():
    AgentApp(Agent.from_config()).run()


if __name__ == "__main__":
    main()
