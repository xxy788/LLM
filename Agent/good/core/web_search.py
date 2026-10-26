"""百度千帆「智能搜索生成」API 封装，与 UI 无关。

鉴权信息从 config.ini 的 [search] 段读取（baidu_qianfan 为 API Key），
不在代码中硬编码。所有失败都转换成可读的错误字符串返回，
以便作为工具调用结果交还给 LLM。
"""

import json

import requests

from .config import load_search_config

TIMEOUT = 30


def search_web(query, top_k=10):
    """搜索互联网并返回「摘要 + 参考来源」文本；失败时返回以「错误：」开头的信息。"""
    query = (query or "").strip()
    if not query:
        return "错误：搜索关键词不能为空"

    try:
        cfg = load_search_config()
    except Exception as exc:
        return f"错误：读取搜索配置失败：{exc}"
    if not cfg["api_key"]:
        return "错误：未配置搜索 API Key，请在 config.ini 的 [search] 段设置 baidu_qianfan"

    payload = {
        "messages": [{"role": "user", "content": query}],
        "model": cfg["model"],
        "search_source": "baidu_search_v2",
        "resource_type_filter": [{"type": "web", "top_k": _clamp_top_k(top_k)}],
        "stream": False,
    }

    try:
        response = requests.post(
            cfg["base_url"],
            headers={
                "Authorization": f"Bearer {cfg['api_key']}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        return f"错误：网络请求失败：{exc}"

    if response.status_code != 200:
        return f"错误：搜索 API 返回 HTTP {response.status_code}：{_error_message(response)}"

    try:
        data = response.json()
    except ValueError:
        return f"错误：搜索 API 返回内容不是合法 JSON：{response.text[:200]}"

    return _format_result(query, data)


def _clamp_top_k(top_k):
    try:
        value = int(top_k)
    except (TypeError, ValueError):
        value = 10
    return max(1, min(value, 20))


def _error_message(response):
    """优先提取 API 返回的 error.message。"""
    try:
        return json.loads(response.text)["error"]["message"]
    except (ValueError, KeyError, TypeError):
        return response.text[:300]


def _body_error_message(data):
    """兼容 {"code": ..., "message": ...} 与 {"error": {"message": ...}} 两种错误体。"""
    error = data.get("error")
    if isinstance(error, dict):
        return error.get("message") or json.dumps(error, ensure_ascii=False)
    message = data.get("message") or json.dumps(data, ensure_ascii=False)
    code = data.get("code")
    return f"{message}（{code}）" if code else message


def _format_result(query, data):
    choices = data.get("choices") or []
    if not choices:
        # 千帆部分错误以 HTTP 200 + 错误体返回
        if data.get("code") or data.get("error"):
            return f"错误：搜索 API 返回错误：{_body_error_message(data)}"
        return f"错误：搜索 API 未返回结果：{json.dumps(data, ensure_ascii=False)[:300]}"

    summary = ((choices[0].get("message") or {}).get("content") or "").strip()
    references = data.get("references") or []
    web_refs = [ref for ref in references if (ref.get("type") or "web") == "web" and ref.get("url")]

    lines = [f"搜索关键词：{query}", f"搜索摘要：{summary or '（无）'}"]
    if web_refs:
        lines.append("参考来源：")
        for index, ref in enumerate(web_refs, 1):
            title = (ref.get("title") or ref.get("web_anchor") or "").strip() or "(无标题)"
            lines.append(f"{index}. {title} - {ref['url']}")
    else:
        lines.append("参考来源：（无）")
    return "\n".join(lines)
