# -*- coding: utf-8 -*-
"""核对新简介与脚注。"""
import sqlite3, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

for slug in ("人物/赵活", "人物/叶云裳", "势力/唐门", "势力/锦香宫",
             "地点/崆峒山", "地点/唐门", "人物/樊啸天"):
    r = c.execute("select name,lead,sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        print(slug, "（无）"); continue
    secs = json.loads(r[2])
    print(f"\n{slug}｜{r[0]}")
    print("  导语:", (r[1] or "")[:90])
    for s in secs:
        print(f"  · {s['h']}：{len(s.get('rows') or [])} 行")
        for row in (s.get("rows") or [])[:3]:
            print(f"      {row.get('note','')[:26]}｜{row.get('quote','')[:40]}")

n = 0
for (slug,) in c.execute("select slug from pages where type in ('人物','势力','地点')"):
    r = c.execute("select sections,lead from pages where slug=?", (slug,)).fetchone()
    if "全都发生" in (r[0] or "") or "全都发生" in (r[1] or ""):
        n += 1
        print("残留元叙述:", slug)
print("\n残留「全都发生」页数:", n)
