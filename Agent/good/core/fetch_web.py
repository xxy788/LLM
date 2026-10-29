"""Fetch a webpage with the local curi program and extract its main content."""

import subprocess
from urllib.parse import urlparse

TIMEOUT = 30


def fetch_web(url):
    """Return a webpage's main content as Markdown, or a readable error."""
    url = (url or "").strip()
    if not url:
        return "错误：网页 URL 不能为空"

    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        return "错误：请输入有效的 HTTP 或 HTTPS 网页 URL"

    try:
        result = subprocess.run(
            ["curi", url],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT,
            check=False,
            shell=False,
        )
    except FileNotFoundError:
        return "错误：未找到本地 curi 程序，请确认其已安装并位于 PATH 中"
    except subprocess.TimeoutExpired:
        return f"错误：访问网页超时（超过 {TIMEOUT} 秒）：{url}"
    except OSError as exc:
        return f"错误：启动 curi 失败：{exc}"

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()[:500]
        return f"错误：网页访问失败（curi 退出码 {result.returncode}）：{detail or '无错误详情'}"

    html = result.stdout
    if not html.strip():
        return f"错误：网页访问失败，curi 未返回 HTML 内容：{url}"

    try:
        import trafilatura

        markdown = trafilatura.extract(
            html,
            url=url,
            output_format="markdown",
            include_links=True,
            include_tables=True,
            include_comments=False,
        )
    except Exception as exc:
        return f"错误：解析网页 HTML 失败：{exc}"

    if not markdown or not markdown.strip():
        return f"错误：无法从网页中提取正文：{url}"

    return f"原始 URL：{url}\n\n{markdown.strip()}"