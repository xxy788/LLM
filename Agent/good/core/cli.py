"""Local CLI execution helpers."""

import json
import subprocess

TIMEOUT = 30
MAX_OUTPUT_CHARS = 8000


def parse_cli_call(arguments):
    """Parse and validate the command and string argument list."""
    try:
        payload = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return None, None, "错误：RunCli 参数不是合法的 JSON"

    if not isinstance(payload, dict):
        return None, None, "错误：RunCli 参数必须是 JSON 对象"

    command = payload.get("command")
    args = payload.get("args")
    if not isinstance(command, str) or not command.strip():
        return None, None, "错误：command 必须是非空程序名称"
    if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
        return None, None, "错误：args 必须是字符串列表"

    return command, args, None


def _truncate_output(output):
    if len(output) <= MAX_OUTPUT_CHARS:
        return output, False
    omitted = len(output) - MAX_OUTPUT_CHARS
    return f"{output[:MAX_OUTPUT_CHARS]}\n...[已截断，省略 {omitted} 个字符]", True


def _decode_output(output):
    if output is None:
        return ""
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return output


def run_cli(command, args):
    """Run a confirmed CLI command without a shell and return bounded output."""
    argv = [command, *args]
    try:
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT,
            check=False,
            shell=False,
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        exit_code = str(result.returncode)
    except subprocess.TimeoutExpired as exc:
        stdout = _decode_output(exc.stdout)
        stderr = _decode_output(exc.stderr)
        stderr = f"{stderr}\n命令执行超时（{TIMEOUT} 秒）".strip()
        exit_code = "未取得（超时）"
    except OSError as exc:
        stdout = ""
        stderr = f"{type(exc).__name__}: {exc}"
        exit_code = "未启动"

    stdout, stdout_truncated = _truncate_output(stdout)
    stderr, stderr_truncated = _truncate_output(stderr)
    return "\n".join(
        [
            f"命令：{json.dumps(argv, ensure_ascii=False)}",
            f"退出码：{exit_code}",
            f"stdout（截断：{'是' if stdout_truncated else '否'}）：\n{stdout or '（空）'}",
            f"stderr（截断：{'是' if stderr_truncated else '否'}）：\n{stderr or '（空）'}",
        ]
    )