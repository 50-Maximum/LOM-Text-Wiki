# -*- coding: utf-8 -*-
"""用 DeepSeek API 批量通读分块文本，抽取实体台账。"""
import os, json, time, re, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

READ = r"D:\LegendOfMortal Wiki\data\read"
OUT = r"D:\LegendOfMortal Wiki\data\ledger"
os.makedirs(OUT, exist_ok=True)
KEY = os.environ["DEEPSEEK_API_KEY"]
URL = "https://api.deepseek.com/chat/completions"

SYS = """你是游戏《活侠传》的资料整理员。阅读给定剧情文本，抽取可做 wiki 条目的实体。
只输出 JSON：{"entries":[{"type":"势力|地点|人物|关系|书物|事件","name":"...","note":"...","evidence":"原文短引"}]}
规则：
1. type 只能是六类之一；关系条目的 name 写成「A—B」。
2. note 用一两句中文说明，不复述空话。
3. evidence 必须是原文中的短句（不超过40字），用于核对。
4. 只收文本中确实出现、有信息量的事物；路人和一次性称呼不收。
5. 每块最多 60 条，重复的合并。"""

def parts():
    out = []
    for fn in os.listdir(READ):
        if not fn.endswith(".txt"):
            continue
        base = fn[:-4]
        if ".part" not in base:
            # 只处理未手动读过的整章
            if base in ("序章", "第0章", "第1章"):
                continue
        else:
            ch, p = base.split(".part")
            if ch == "第2章" and int(p) <= 3:
                continue
        out.append(fn)
    return sorted(out)

def call(fn):
    txt = open(os.path.join(READ, fn), encoding="utf-8").read()
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": SYS},
                     {"role": "user", "content": "章节分块：" + fn + "\n\n" + txt}],
        "temperature": 0.2,
        "max_tokens": 4000,
        "response_format": {"type": "json_object"},
    }).encode("utf-8")
    req = urllib.request.Request(URL, data=body, headers={
        "Authorization": "Bearer " + KEY,
        "Content-Type": "application/json",
    })
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.loads(r.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            m = re.search(r"\{.*\}", content, re.S)
            obj = json.loads(m.group(0)) if m else {"entries": []}
            ents = obj.get("entries", [])
            json.dump(ents, open(os.path.join(OUT, fn.replace(".txt", ".json")), "w",
                                 encoding="utf-8"), ensure_ascii=False, indent=1)
            return fn, len(ents)
        except Exception as e:
            if attempt == 3:
                return fn, "ERR " + str(e)[:120]
            time.sleep(3 * (attempt + 1))
    return fn, "ERR"

todo = [f for f in parts() if not os.path.exists(os.path.join(OUT, f.replace(".txt", ".json")))]
print("todo", len(todo), "of", len(parts()))
done = 0
with ThreadPoolExecutor(max_workers=4) as ex:
    futs = {ex.submit(call, f): f for f in todo}
    for fu in as_completed(futs):
        fn, n = fu.result()
        done += 1
        print(f"[{done}/{len(todo)}] {fn} -> {n}", flush=True)
print("ALL DONE")
