# -*- coding: utf-8 -*-
"""核对新结构：地点页、子地点表、武学/战技分类。"""
import sqlite3, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("place_children:", c.execute("select count(*) from place_children").fetchone()[0])
print("地点总数:", c.execute("select count(*) from pages where type='地点'").fetchone()[0],
      "顶层:", c.execute("select count(*) from pages where type='地点' and slug not in (select slug from place_children)").fetchone()[0])

for slug in ("地点/唐门", "人物/赵活", "人物/唐铮"):
    r = c.execute("select name,lead,sections from pages where slug=?", (slug,)).fetchone()
    secs = json.loads(r[2])
    print(f"\n{slug}｜{r[0]}")
    print("  导语:", (r[1] or "")[:80])
    for s in secs:
        print(f"  · {s['h']}：{len(s.get('rows') or [])} 行")
        for row in (s.get("rows") or [])[:4]:
            print("      ", row.get("note", "")[:50])

print("\n武学样本:", [x[0] for x in c.execute("select name from pages where type='武学' limit 6")])
print("战技样本:", [x[0] for x in c.execute("select name from pages where type='战技' limit 6")])
print("物品样本:", [x[0] for x in c.execute("select name from pages where type='物品' limit 6")])
