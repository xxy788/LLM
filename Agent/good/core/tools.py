"""LLM 工具定义（schema）与工具分发执行，与 UI 无关。"""

import json

from . import cli, fetch_web, file_ops, web_search

tools = [
    {
        "type": "function",
        "function": {
            "name": "getDate",
            "description": "获取当前电脑的日期和时间，通过调用本地date命令实现",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getcwd",
            "description": "获取当前工作目录",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listFiles",
            "description": "列出指定目录下所有文件和子目录，不递归",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "目录路径，缺省为当前目录",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getFileType",
            "description": "获取指定文件的文件类型（扩展名和MIME类型）",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件路径",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "readFile",
            "description": "获取指定纯文本文件的内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件路径",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "createFile",
            "description": "根据指定的目录和文件名创建新文件，可选写入初始内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "新文件所在目录路径，缺省为当前目录",
                    },
                    "filename": {
                        "type": "string",
                        "description": "文件名，例如 note.txt",
                    },
                    "content": {
                        "type": "string",
                        "description": "文件初始内容，缺省为空文件",
                    },
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "editFile",
            "description": "编辑指定纯文本文件的内容，用新内容覆盖原文件，文件必须已存在",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件路径",
                    },
                    "content": {
                        "type": "string",
                        "description": "编辑后的新内容，将覆盖原内容",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "createDirectory",
            "description": "创建新目录（含多级目录）",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "目录路径",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "deleteDirectory",
            "description": "删除指定目录及其全部内容（支持非空目录）",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "目录路径",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "deleteFile",
            "description": "删除指定文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件路径",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "searchWeb",
            "description": "通过百度千帆智能搜索生成API搜索互联网实时信息，返回搜索摘要及参考来源（标题、URL）",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词或问题",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回的网页结果数量，1-20，缺省为10",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetchWeb",
            "description": "获取指定网页的主要正文并转换为 Markdown，保留标题、段落、列表、表格和链接",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要提取正文的 HTTP 或 HTTPS 网页 URL",
                    },
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "loadSkill",
            "description": "加载指定 Skill 的完整说明，或读取该 Skill 目录内的附加文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "已发现的 Skill 名称",
                    },
                    "filename": {
                        "type": "string",
                        "description": "可选，Skill 目录内文件的路径或文件名",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "RunCli",
            "description": "在用户逐次确认后运行本地命令行程序，并返回标准输出、标准错误和退出码",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "本地程序名称或可执行文件路径",
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "传给程序的参数列表，每一项作为独立参数传递",
                    },
                },
                "required": ["command", "args"],
            },
        },
    },
]


def run_tool(name, arguments, cli_approved=False, skills=None):
    try:
        args = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return "错误：工具参数不是合法的JSON"
    if name == "getDate":
        return file_ops.get_date()
    if name == "getcwd":
        return file_ops.get_cwd()
    if name == "listFiles":
        return file_ops.list_files(args.get("path", "."))
    if name == "getFileType":
        return file_ops.get_file_type(args["path"])
    if name == "readFile":
        return file_ops.read_file(args["path"])
    if name == "createFile":
        return file_ops.create_file(args.get("directory", ""), args["filename"], args.get("content", ""))
    if name == "editFile":
        return file_ops.edit_file(args["path"], args["content"])
    if name == "createDirectory":
        return file_ops.create_directory(args["path"])
    if name == "deleteDirectory":
        return file_ops.delete_directory(args["path"])
    if name == "deleteFile":
        return file_ops.delete_file(args["path"])
    if name == "rename":
        return file_ops.rename_entry(args["path"], args["newName"])
    if name == "searchWeb":
        return web_search.search_web(args.get("query", ""), args.get("top_k", 10))
    if name == "fetchWeb":
        return fetch_web.fetch_web(args.get("url", ""))
    if name == "loadSkill":
        skill_name = args.get("name")
        if not isinstance(skill_name, str):
            return "错误：loadSkill 的 name 参数必须是字符串"
        skill = (skills or {}).get(skill_name)
        if skill is None:
            return f"错误：未找到 Skill: {skill_name}"
        return skill.load_file(args.get("filename"))
    if name == "RunCli":
        command, command_args, error = cli.parse_cli_call(arguments)
        if error:
            return error
        if not cli_approved:
            return "错误：RunCli 必须先获得用户确认"
        return cli.run_cli(command, command_args)
    return f"unknown tool: {name}"
