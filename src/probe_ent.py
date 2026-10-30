# -*- coding: utf-8 -*-
import sqlite3, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
for name in ("千灯楼", "唐门", "赵活", "虞小梅", "南宫禹"):
    r = c.execute("select type,intro,aliases,tags,mentions,chapters from entities where name=?", (name,)).fetchone()
    if not r:
        print(name, "MISSING"); continue
    print("=" * 72)
    print(f"{r[0]} · {name}  （{r[4]} 条笔记 / {len(json.loads(r[5]))} 章）")
    print(f"别名 {r[2]}  标签 {r[3]}")
    print(r[1])
print()
print("-- 空简介实体数 --", c.execute("select count(*) from entities where intro=''").fetchone()[0])
print("-- 简介字数分布 --")
for r in c.execute("select min(length(intro)),avg(length(intro)),max(length(intro)) from entities where intro<>''"):
    print("  min/avg/max:", [round(x, 1) if isinstance(x, float) else x for x in r])
