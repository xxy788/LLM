import configparser
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

c = configparser.ConfigParser()
c.read("config.ini", encoding="utf-8")
s = c["llm"]

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


def get_date():
    r = subprocess.run("date /t & time /t", shell=True, capture_output=True)
    raw = r.stdout
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("mbcs", errors="replace")
    return text.strip()


def get_cwd():
    return os.getcwd()


def list_files(path="."):
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        return f"错误：目录不存在: {path}"
    lines = []
    with os.scandir(path) as it:
        for entry in sorted(it, key=lambda e: e.name.lower()):
            lines.append(f"[目录] {entry.name}" if entry.is_dir() else f"[文件] {entry.name}")
    if not lines:
        return f"目录为空: {path}"
    return "\n".join(lines)


def get_file_type(path):
    if not os.path.isfile(path):
        return f"错误：文件不存在: {path}"
    ext = os.path.splitext(path)[1]
    mime, _ = mimetypes.guess_type(path)
    return f"扩展名: {ext or '(无)'}，MIME类型: {mime or '未知'}"


def read_file(path):
    if not os.path.isfile(path):
        return f"错误：文件不存在: {path}"
    with open(path, "rb") as f:
        raw = f.read()
    if b"\x00" in raw[:8192]:
        return f"错误：该文件不是纯文本文件，拒绝读取: {path}"
    text = None
    for enc in ("utf-8", "gb18030"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        text = raw.decode("utf-8", errors="replace")
    if len(text) > 50000:
        text = text[:50000] + "\n……(内容过长，已截断)"
    return text


def create_file(directory, filename, content=""):
    path = os.path.join(directory, filename) if directory else filename
    path = os.path.abspath(path)
    if os.path.exists(path):
        return f"错误：文件已存在: {path}"
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"已创建文件: {path}"


def edit_file(path, content):
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        return f"错误：文件不存在: {path}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"已保存文件: {path}"


def create_directory(path):
    path = os.path.abspath(path)
    if os.path.exists(path):
        return f"错误：路径已存在: {path}"
    os.makedirs(path)
    return f"已创建目录: {path}"


def delete_directory(path):
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        return f"错误：目录不存在: {path}"
    shutil.rmtree(path)
    return f"已删除目录（含所有内容）: {path}"


def delete_file(path):
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        return f"错误：文件不存在: {path}"
    os.remove(path)
    return f"已删除文件: {path}"


def rename_entry(path, new_name):
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return f"错误：文件或目录不存在: {path}"
    if os.path.isabs(new_name) or os.sep in new_name or "/" in new_name:
        target = os.path.abspath(new_name)
    else:
        target = os.path.join(os.path.dirname(path), new_name)
    if target == path:
        return "错误：新名称与原名称相同"
    if os.path.exists(target):
        return f"错误：目标已存在: {target}"
    parent = os.path.dirname(target)
    if parent and not os.path.isdir(parent):
        return f"错误：目标所在目录不存在: {parent}"
    os.rename(path, target)
    return f"已重命名: {path} -> {target}"


def run_tool(name, arguments):
    try:
        args = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return "错误：工具参数不是合法的JSON"
    if name == "getDate":
        return get_date()
    if name == "getcwd":
        return get_cwd()
    if name == "listFiles":
        return list_files(args.get("path", "."))
    if name == "getFileType":
        return get_file_type(args["path"])
    if name == "readFile":
        return read_file(args["path"])
    if name == "createFile":
        return create_file(args.get("directory", ""), args["filename"], args.get("content", ""))
    if name == "editFile":
        return edit_file(args["path"], args["content"])
    if name == "createDirectory":
        return create_directory(args["path"])
    if name == "deleteDirectory":
        return delete_directory(args["path"])
    if name == "deleteFile":
        return delete_file(args["path"])
    if name == "rename":
        return rename_entry(args["path"], args["newName"])
    return f"unknown tool: {name}"


def main():
    messages = []
    while True:
        print("please input your prompt：")
        prompt = input()
        print("————")

        messages.append({"role": "user", "content": prompt})
        while True:
            r = requests.post(
                s["base_url"],
                headers={"Authorization": f"Bearer {s['api_key']}", "Content-Type": "application/json"},
                json={"model": s["model"], "messages": messages, "tools": tools, "stream": True},
                stream=True,
            )
            reply = ""
            calls = {}
            for line in r.iter_lines():
                if line.startswith(b"data: ") and line != b"data: [DONE]":
                    delta = json.loads(line[6:])["choices"][0].get("delta", {})
                    t = delta.get("content") or ""
                    if t:
                        reply += t
                        print(t, end="", flush=True)
                    for tc in delta.get("tool_calls") or []:
                        call = calls.setdefault(
                            tc.get("index", 0),
                            {"id": "", "type": "function", "function": {"name": "", "arguments": ""}},
                        )
                        if tc.get("id"):
                            call["id"] = tc["id"]
                        f = tc.get("function") or {}
                        call["function"]["name"] += f.get("name") or ""
                        call["function"]["arguments"] += f.get("arguments") or ""
            print()

            call_list = [calls[i] for i in sorted(calls)]
            if not call_list:
                messages.append({"role": "assistant", "content": reply})
                break

            messages.append({"role": "assistant", "content": reply, "tool_calls": call_list})
            for call in call_list:
                result = run_tool(call["function"]["name"], call["function"]["arguments"])
                print(f"[tool {call['function']['name']}] {result}")
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})


if __name__ == "__main__":
    main()
