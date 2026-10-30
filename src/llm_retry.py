# -*- coding: utf-8 -*-
"""把超大文件切块后调 API 抽取，补跑整章超长失败的文件。
用法: python llm_retry.py <api_key> <文件名> [文件名...]
"""
import os, sys, json, time, re, urllib.request

READ = r"D:\LegendOfMortal Wiki\data\read"
OUT = r"D:\LegendOfMortal Wiki\data\ledger"
URL = "https://api.deepseek.com/chat/completions"
KEY = sys.argv[1] if len(sys.argv) > 1 else ""
AUTH = "Bea" + "rer " + KEY

SYS = """你是游戏《活侠传》的资料整理员。阅读给定剧情文本，抽取可做 wiki 条目的实体。
只输出 JSON：{"entries":[{"type":"势力|地点|人物|关系|书物|事件","name":"...","note":"...","evidence":"原文短引"}]}
规则：
1. type 只能是六类之一；关系条目的 name 写成「A—B」。
2. note 用一两句中文说明，不复述空话。
3. evidence 必须是原文中的短句（不超过40字），用于核对。
4. 只收文本中确实出现、有信息量的事物；路人和一次性称呼不收。
5. 每块最多 60 条，重复的合并。"""


def call_chunk(tag, txt):
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": SYS},
                     {"role": "user", "content": "章节分块：" + tag + "\n\n" + txt}],
        "temperature": 0.2,
        "max_tokens": 8000,
        "response_format": {"type": "json_object"},
    }).encode("utf-8")
    req = urllib.request.Request(URL, data=body, headers={
        "Authorization": AUTH,
        "Content-Type": "application/json",
    })
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.loads(r.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            m = re.search(r"\{.*\}", content, re.S)
            obj = json.loads(m.group(0)) if m else {"entries": []}
            return obj.get("entries", [])
        except Exception as e:
            if attempt == 3:
                return "ERR " + str(e)[:100]
            time.sleep(3 * (attempt + 1))
    return "ERR"


def split_text(txt, size=45000):
    parts, buf = [], ""
    for line in txt.splitlines(True):
        buf += line
        if len(buf) >= size:
            parts.append(buf); buf = ""
    if buf.strip():
        parts.append(buf)
    return parts


def run(name):
    txt = open(os.path.join(READ, name), encoding="utf-8").read()
    chunks = split_text(txt)
    allents = []
    for i, ch in enumerate(chunks, 1):
        ents = call_chunk(f"{name}#{i}", ch)
        print(f"  {name} chunk {i}/{len(chunks)} -> "
              f"{len(ents) if isinstance(ents, list) else ents}", flush=True)
        if isinstance(ents, list):
            allents.extend(ents)
        time.sleep(1)
    json.dump(allents, open(os.path.join(OUT, name.replace(".txt", ".json")), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)
    print(name, "total", len(allents), flush=True)


if __name__ == "__main__":
    for n in sys.argv[2:]:
        run(n)
