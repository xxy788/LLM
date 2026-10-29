"""配置加载：所有前端共享同一配置来源。"""

import configparser
import os

DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.ini"
)


def load_llm_config(path=None):
    path = path or DEFAULT_CONFIG_PATH
    c = configparser.ConfigParser()
    c.read(path, encoding="utf-8")
    s = c["llm"]
    return {"base_url": s["base_url"], "api_key": s["api_key"], "model": s["model"]}
