# -*- coding: utf-8 -*-
"""给没有引文的出处补上该场景首句，避免脚注只剩标题。"""
import sqlite3, json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))

def first_line(sc):
    r = c.execute("select speaker,text from lines where script=? order by seq limit 1", (sc,)).fetchone()
    if not r:
        return ""
    t = (r[1] or "").replace("\n", " ").strip()
    return t[:44]

for fn in ("intros_char.json", "intros_world.json"):
    p = os.path.join(BASE, "data", fn)
    data = json.load(open(p, encoding="utf-8"))
    n = 0
    for key, v in data.items():
        if not isinstance(v, dict):
            continue
        for s in v.get("sources", []):
            if s.get("script") and not s.get("quote"):
                q = first_line(s["script"])
                if q:
                    s["quote"] = q
                    n += 1
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(fn, "补引文", n)
