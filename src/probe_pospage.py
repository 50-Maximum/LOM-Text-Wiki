# -*- coding: utf-8 -*-
"""看现有「地图事件」页的结构，判断未映射的 25 个该怎么挂。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
rows = list(c.execute("""select slug,name,infobox,sections from pages
                         where type='地图事件' limit 3"""))
for slug, name, ib, sec in rows:
    print("=" * 70)
    print(slug, "|", name)
    print("infobox:", (ib or "")[:300])
    print("sections:", (sec or "")[:500])
print("\n地图事件总数:", c.execute("select count(*) from pages where type='地图事件'").fetchone()[0])
print("\n示例 slug:", [r[0] for r in c.execute(
    "select slug from pages where type='地图事件' limit 6")])
