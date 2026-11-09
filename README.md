# LLM 实践工作区

个人 LLM 应用学习与实践工作区。主要项目是 [`Agent/good`](Agent/good)，一个基于 LLM 的文件助手，采用 core（业务逻辑）与 TUI（终端界面）分层，并支持 Agent Skills。

## 目录结构

```text
LLM/
├── Agent/
│   ├── good/                  # 文件助手 Agent
│   │   ├── core/              # Agent、工具和 Skill 加载逻辑
│   │   ├── tui/               # Textual 终端界面
│   │   ├── tests/             # 自动化测试
│   │   ├── config.example.ini # 不含真实密钥的配置模板
│   │   └── main.py            # 启动入口
│   ├── Practice01/            # LLM 对话练习
│   └── Practice02/            # 文件工具 Agent 练习
├── anythingLLMMCP/            # AnythingLLM MCP 服务
├── anythingLLMServer/         # AnythingLLM 上传页面
└── pethospitalMCP/            # 宠物医院 MCP 服务
```

## Agent/good

### 安装与启动

在仓库根目录执行以下 PowerShell 命令。这样启动时，Skill 会从仓库根目录的 `.agents/skills/` 发现：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r Agent/good/requirements.txt
```

首次启动时，程序会在当前目录创建完整的 mock `config.ini` 并显示配置提示。编辑该文件，填入服务地址、模型名和 API key 后重启：

```powershell
python Agent/good/main.py
```

macOS/Linux 激活虚拟环境的命令是 `source .venv/bin/activate`；配置文件路径和启动命令相同。

### 配置

`Agent/good/config.ini` 中的 `[llm]` 用于对话接口；`[search]` 中的 `baidu_qianfan` 用于 `searchWeb`，未配置搜索 key 时该功能不可用。配置模板在 [`Agent/good/config.example.ini`](Agent/good/config.example.ini)，应只放占位值，不放真实凭据。

`fetchWeb` 还需要本机安装 `curi` 命令并确保它位于 `PATH` 中；其他 Agent 功能不依赖它。

### MCP 服务器

`good` 会从当前工作目录及其父目录查找 `.mcp.json`，读取其中的 `mcpServers` 配置。支持 stdio 子进程和 Streamable HTTP；启动后发现的 MCP 工具会提供给 Agent，输入 `/mcp` 可查看连接状态和工具列表。stdio 配置示例：

```json
{
   "mcpServers": {
      "example": {
         "type": "stdio",
         "command": "python",
         "args": ["path/to/server.py"],
         "env": {}
      }
   }
}
```

HTTP 服务可配置为 `{"type":"streamable-http","url":"https://example.invalid/mcp"}`，需要请求头时可添加 `headers` 对象。`.mcp.json` 不在默认忽略规则中；提交前检查配置是否含有令牌、密钥或其他凭据，避免将其提交到仓库。

### Agent Skills

Skill 根目录取决于启动程序时的当前工作目录。以上述仓库根目录启动方式为例，将 Skill 放在：

```text
.agents/skills/<skill-name>/SKILL.md
```

`SKILL.md` 需要以 YAML frontmatter 声明 `name` 和 `description`：

```markdown
---
name: example
description: 简要说明此 Skill 的用途
---

在这里编写 Skill 指令。
```

启动时只读取 Skill 名称和描述；模型需要完整指令或附加文件时，会调用 `loadSkill`。附加文件只能从该 Skill 目录内读取；只提供文件名且存在多个匹配时，工具会返回候选路径。

`good` 默认通过 `[agent] skill_dirs` 注册外置 Skill。工作区中的 Guizang PPT Skill 已配置为 `office/mulu/.agent/skills/guizang-ppt-skill_#SULP#_0lea6z/guizang-ppt-skill`，其 HTML 模板、`references/` 和校验脚本均从原目录按需读取，不需要复制。

项目根目录的 `AGENTS.md` 会在会话创建时作为 system 消息注入并写入会话日志；后续轮次复用该消息，恢复会话也不会重复注入。会话历史保存在 `.agents/sessions/`，已加入 `.gitignore`。

### Slash 命令

输入 `/` 可显示命令补全；使用上下键选择，Enter 补全，再按 Enter 执行。支持 `/new`（保存并新建）、`/resume`（键盘选择历史会话）、`/save`、`/quit`、`/compact`、`/help`、`/status` 和 `/mcp`。`Ctrl+Q` 也会保存并退出。

### 上下文压缩与历史检索

TUI 状态栏显示当前上下文估算/接口用量、模型窗口和占比。达到窗口的 70% 后，普通提示会被暂停；输入 `/compact` 可将完整消息归档到 `.agents/context/`，再由 LLM 生成摘要并替换历史。摘要失败时原会话保持不变。

`recallContext` 可按关键词检索归档原文，也可指定归档编号。归档包含完整对话及工具调用，应留在本地；`.agents/context/` 已加入 `.gitignore`。

`[llm]` 可通过 `context_window = 32k` 或 `context_window = 128000` 指定窗口。未配置时会尝试从模型名中的 `32k` 等后缀识别；无法识别则按 128k 处理，并在状态栏标记“默认”。

### 自动化测试

在仓库根目录运行：

```powershell
python -m unittest discover -s Agent/good/tests -v
```

## 上传 GitHub 前检查密钥

1. 本地凭据使用 `config.ini`、`.env` 或独立凭据文件保存；这些文件已加入 [.gitignore](.gitignore)。`config.example.ini` 和 `.env.example` 可提交，但内容必须是占位值。
2. 不要把 API key 写进 Python、HTML、Markdown 示例、截图或提交信息中，也不要把真实密钥粘贴到公开 issue。
3. 推送前在仓库根目录检查忽略规则和暂存内容：

   ```powershell
   git check-ignore -v Agent/good/config.ini
   git status --short
   git diff --cached --name-only
   ```

4. `.gitignore` 只对未跟踪文件生效，不能自动从 Git 历史中移除已经提交的密钥。若 key 曾被提交，立即在服务商后台吊销并重新生成；再清理仓库历史后推送。
