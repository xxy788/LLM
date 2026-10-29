"""配置加载：所有前端共享同一配置来源。"""

import configparser
import os

DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.ini"
)

SEARCH_ENDPOINT = "https://qianfan.baidubce.com/v2/ai_search/chat/completions"


def load_llm_config(path=None):
    if path is None:
        path = DEFAULT_CONFIG_PATH
    c = configparser.ConfigParser()
    c.read(path, encoding="utf-8")
    s = c["llm"]
    return {"base_url": s["base_url"], "api_key": s["api_key"], "model": s["model"]}


def load_search_config(path=None):
    """读取 [search] 段。未配置 api_key 时返回空字符串，由调用方给出错误提示。"""
    if path is None:
        path = DEFAULT_CONFIG_PATH
    c = configparser.ConfigParser()
    c.read(path, encoding="utf-8")
    return {
        "api_key": c.get("search", "baidu_qianfan", fallback="").strip(),
        "base_url": c.get("search", "base_url", fallback=SEARCH_ENDPOINT),
        # 搜索模型缺省沿用对话模型
        "model": c.get("search", "model", fallback=c.get("llm", "model", fallback="ernie-4.5-turbo-32k")),
    }
