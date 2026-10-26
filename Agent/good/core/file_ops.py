"""文件系统操作核心函数，与 UI 无关，返回字符串结果。"""

import mimetypes
import os
import shutil
import subprocess


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
