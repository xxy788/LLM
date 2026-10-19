import configparser
import json
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
    }
]


def get_date():
    r = subprocess.run("date /t & time /t", shell=True, capture_output=True)
    raw = r.stdout
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("mbcs", errors="replace")
    return text.strip()


def run_tool(name):
    if name == "getDate":
        return get_date()
    return f"unknown tool: {name}"


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
            result = run_tool(call["function"]["name"])
            print(f"[tool {call['function']['name']}] {result}")
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
