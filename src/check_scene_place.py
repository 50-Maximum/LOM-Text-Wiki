# -*- coding: utf-8 -*-
"""看场景页里地点字段落在哪，并抽验三场改判是否生效。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for slug in ("场景/ch5_4_2", "场景/S0703_01", "场景/S0101_01"):
    r = c.execute("select slug,name,infobox,sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        print("缺", slug)
        continue
    inf = json.loads(r["infobox"] or "{}")
    print("=" * 60)
    print(slug, "|", r["name"])
    for k, v in inf.items():
        print("   %s = %s" % (k, v))
    secs = json.loads(r["sections"] or "[]")
    print("   sections:", [s.get("h") for s in secs])
