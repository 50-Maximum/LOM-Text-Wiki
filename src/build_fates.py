# -*- coding: utf-8 -*-
"""角色命运线索：旗标标签里带「死/活/嫁/离开/加入/成为/叛」等结果词的，按角色归类。

写 data/fates_raw.json 供人工定稿。
"""
import os, sys, io, sqlite3, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))

names = set()
for (n,) in c.execute("select distinct name from names"):
    if n and len(n) <= 5:
        names.add(n)
for (n,) in c.execute("select name from entities where type='人物'"):
    if n and len(n) <= 6:
        names.add(n)

FATE = ("死", "亡", "活", "嫁", "娶", "离开", "离唐门", "加入", "成为", "叛", "投",
        "失踪", "失忆", "残", "救", "杀", "拜", "继任", "掌门", "退隐", "结缘",
        "同行", "留下", "回去", "回唐门", "远走", "断", "决裂", "和好", "成亲")

rows = []
for flag, label in c.execute("select flag,label from flaginfo"):
    lab = label or ""
    hitnames = [n for n in names if n in lab]
    if not hitnames:
        continue
    if not any(w in lab for w in FATE):
        continue
    sets = c.execute("""select script,seq,value,branch from flags
                        where flag=? order by script,seq""", (flag,)).fetchall()
    sets2 = [{"script": s, "seq": q, "value": v, "branch": b[:100]} for s, q, v, b in sets]
    rows.append({"flag": flag, "label": lab, "names": hitnames, "sets": sets2})

# 按角色聚合
by = collections.defaultdict(list)
for r in rows:
    for n in r["names"]:
        by[n].append(r)

out = os.path.join(BASE, "data", "fates_raw.json")
json.dump(by, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("命中角色", len(by), "旗标条目", len(rows))
for n in sorted(by, key=lambda x: -len(by[x]))[:20]:
    print(f"\n== {n}（{len(by[n])}）")
    for r in by[n][:6]:
        print(f"   {r['flag']} {r['label'][:60]}  设置于 {len(r['sets'])} 处")
