# -*- coding: utf-8 -*-
"""校验并修正 intros_*.json 里的出处：quote 必须真在该场景台词里。

规则：
1. script+quote 能在该场景找到 → 保留
2. 找不到 → 全库搜 quote，改挂到真正出现的场景
3. 仍找不到（多半写的是场景标题）→ 按标题匹配场景，quote 清空，只留场景链接
4. 都找不到 → script 清空，仅保留 note 文字
"""
import sqlite3, sys, io, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))

def norm(s):
    return re.sub(r"\s+", "", s or "")

SCENES = {r[0]: r[1] for r in c.execute("select script,title from scenes")}
TITLE2SC = {}
for sc, ti in SCENES.items():
    if ti:
        TITLE2SC.setdefault(ti, sc)

cache = {}
def lines_of(sc):
    if sc not in cache:
        cache[sc] = norm("".join((t or "") for (t,) in
                                 c.execute("select text from lines where script=?", (sc,))))
    return cache[sc]

def find_anywhere(q):
    qq = norm(q)[:18]
    if len(qq) < 3:
        return ""
    row = c.execute("select script from lines where replace(replace(text,char(10),''),' ','') like ? limit 1",
                    ("%" + qq + "%",)).fetchone()
    return row[0] if row else ""

for fn in ("intros_char.json", "intros_world.json"):
    p = os.path.join(BASE, "data", fn)
    if not os.path.exists(p):
        continue
    data = json.load(open(p, encoding="utf-8"))
    changed = 0
    for key, val in data.items():
        if not isinstance(val, dict):
            continue
        for s in val.get("sources", []):
            sc, q, note = s.get("script", ""), s.get("quote", ""), s.get("note", "")
            ok = bool(sc and q and norm(q) in lines_of(sc))
            if ok:
                continue
            if q:
                alt = find_anywhere(q)
                if alt:
                    s["script"] = alt
                    changed += 1
                    continue
            if note and note in TITLE2SC:
                s["script"] = TITLE2SC[note]
                s["quote"] = ""
                changed += 1
                continue
            if sc and q and not ok:
                s["quote"] = ""
                changed += 1
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(fn, "修正", changed, "条出处")
