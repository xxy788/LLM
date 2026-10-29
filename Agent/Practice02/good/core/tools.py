"""LLM 工具定义（schema）与工具分发执行，与前端无关。"""

import json

from . import file_ops

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
            "name": "rename",
            "description": "重命名文件或目录，也可通过新路径将其移动到其他位置",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "原文件或目录路径",
                    },
                    "newName": {
                        "type": "string",
                        "description": "新名称或新路径；若只是名称则在原目录下重命名，若是路径则移动并重命名",
                    },
                },
                "required": ["path", "newName"],
            },
        },
    },
]


def run_tool(name, arguments):
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
    return f"unknown tool: {name}"
