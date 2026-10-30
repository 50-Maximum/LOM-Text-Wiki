# -*- coding: utf-8 -*-
import sqlite3, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

for slug in ("事件/赵活担保求药斗笠人", "事件/赵活旁观斗笠人跪地"):
    r = c.execute("select infobox,sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        print(slug, "缺"); continue
    print("\n", slug)
    print("  infobox:", r[0])
    print("  sections:", [s["h"] for s in json.loads(r[1])])
    for s in json.loads(r[1]):
        if s["h"] == "时间推导":
            print("  推导:", s["html"][:160])

print("\n人物总数", c.execute("select count(*) from pages where type='人物'").fetchone()[0])
print("事件总数", c.execute("select count(*) from pages where type='事件'").fetchone()[0])
