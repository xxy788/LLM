# LLM 实践工作区

个人 LLM 应用学习与实践工作区。核心项目为 [`Agent/good`](Agent/good)——一个基于 LLM 的文件助手 Agent，采用 **core（业务核心）与 UI（前端界面）分离**的分层架构。

## 目录结构

```
LLM/
├── Agent/
│   ├── good/              # 核心项目：文件助手 Agent（core + tui）
│   │   ├── core/          # 业务核心层（零 UI 依赖，可被任意前端复用）
│   │   ├── tui/           # Textual 终端界面
│   │   ├── config.example.ini  # 配置模板（复制为 config.ini 并填入自己的 key）
│   │   ├── config.ini     # 本地配置（含秘钥，已被 .gitignore 忽略，不会上传）
│   │   └── main.py        # 启动入口
│   ├── Practice01/        # 练习：LLM 对话脚本
│   └── Practice02/        # 练习：文件工具 Agent（单文件版，good 的前身）
├── anythingLLMMCP/        # AnythingLLM MCP 服务
├── anythingLLMServer/     # AnythingLLM 上传页面
└── pethospitalMCP/        # 宠物医院 MCP 服务
```

## 核心项目：Agent/good

### 架构

```
good/
├── core/               # 业务核心层
│   ├── agent.py        # 会话与 LLM 流式交互，产出事件
│   ├── events.py       # 事件协议：TextDelta / ToolCall / ErrorEvent
│   ├── tools.py        # 工具 schema 定义 + 分发执行
│   ├── file_ops.py     # 文件操作实现
│   ├── web_search.py   # 网络搜索实现（千帆智能搜索生成）
│   ├── fetch_web.py    # 网页正文抓取与 Markdown 提取
│   └── config.py       # 配置加载
├── tui/                # Textual 前端：只消费事件做渲染
└── main.py             # 组装入口
```

- **core 与 UI 完全隔离**：core 层通过生成器产出 `TextDelta` / `ToolCall` 事件，不含任何界面代码。
- **前端可替换**：未来新增 `web/`、`desktop/`、`mobile/` 等前端目录时，只需消费同一套事件，core 一行不改。

### 快速开始

```bash
cd Agent/good

# 1. 安装依赖
pip install requests textual trafilatura

# 2. 从模板创建本地配置（不要提交到 GitHub）
copy config.example.ini config.ini    # Windows
# cp config.example.ini config.ini    # macOS / Linux

# 3. 编辑 config.ini，填入你自己的 API key

# 4. 运行
python main.py
```

> `Agent/Practice01`、`Agent/Practice02` 下的脚本同样需要在其所在目录放置 `config.ini`（同样已被 .gitignore 忽略），格式见 `Agent/good/config.example.ini`。

## 安全须知（重要）

1. **所有 `config.ini` 已被 [.gitignore](.gitignore) 忽略**，不会被提交到 GitHub。秘钥只保存在本地。
2. 新环境部署时，**复制 `config.example.ini` 为 `config.ini`** 并填入自己的 key，不要直接改模板。
3. **不要把 API key 写进任何代码、HTML 或脚本文件**——`.gitignore` 只能忽略列出的文件，硬编码在代码里的秘钥会随代码一起上传。
4. **如果秘钥曾经提交过（哪怕后来删除），GitHub 历史中仍然可见**，应立即到服务商后台重置（吊销旧 key、生成新 key）。
5. 推送前可用以下命令做最后检查，确认没有秘钥文件被暂存：

   ```bash
   git status
   git check-ignore -v Agent/good/config.ini
   ```
