"""程序入口：加载配置，组装 core 与 tui 并启动。

未来新增 web / desktop 等前端时，只需新建对应前端包，
并在此处（或各前端的启动脚本中）替换界面入口。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent import Agent
from tui.app import FileAgentTUI


def main():
    FileAgentTUI(Agent.from_config()).run()


if __name__ == "__main__":
    main()
