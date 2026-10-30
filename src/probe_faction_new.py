# -*- coding: utf-8 -*-
"""核对势力层级与脚注。"""
import sqlite3, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("势力页", c.execute("select count(*) from pages where type='势力'").fetchone()[0],
      "顶层", c.execute("select count(*) from pages where type='势力' and slug not in (select slug from place_children)").fetchone()[0])
print("子页", c.execute("select count(*) from place_children where slug like '势力/%'").fetchone()[0])

for slug in ("势力/丐帮", "势力/崆峒派", "势力/泥教", "势力/唐门"):
    r = c.execute("select name,lead,sections from pages where slug=?", (slug,)).fetchone()
    secs = json.loads(r[2])
    print(f"\n{slug}｜{r[0]}")
    print("  导语:", (r[1] or "")[:90])
    for s in secs:
        print(f"  · {s['h']}：{len(s.get('rows') or [])} 行")
        for row in (s.get("rows") or [])[:4]:
            print("      ", row.get("note", "")[:56], "｜", (row.get("quote") or "")[:30])
