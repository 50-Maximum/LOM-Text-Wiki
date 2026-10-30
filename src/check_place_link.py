# -*- coding: utf-8 -*-
"""核对地点名是否指向真实页面：改了名的场景有没有挂到地点页上。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("--- 存在的地点页（崆峒-/唐门-/江陵- 前缀） ---")
for r in c.execute("select name from pages where type='地点' and name like '崆峒-%' order by name"):
    print("   ", r["name"])
print()
for slug in ("地点/崆峒-铁拳巷", "地点/崆峒-夺魄森林"):
    r = c.execute("select sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        print(slug, "缺页")
        continue
    for s in __import__("json").loads(r["sections"] or "[]"):
        if s.get("h") in ("发生场景", "出场场景"):
            rows = s.get("rows") or []
            print("%s 的 %s：%d 条" % (slug, s["h"], len(rows)))
            for x in rows[:5]:
                print("     ", x.get("note") or x.get("title"))
