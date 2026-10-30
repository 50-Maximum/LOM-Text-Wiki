# -*- coding: utf-8 -*-
import sqlite3, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

for slug in ("人物/飞石帮", "人物/魏招弟", "人物/颜师兄", "人物/飞天掌门", "人物/魏菊", "人物/颜疆"):
    r = c.execute("select slug,type from pages where slug=?", (slug,)).fetchone()
    rd = c.execute("select slug from redirects where alias=?", (slug,)).fetchone()
    print(slug, "页面:", r, "重定向:", rd)

e = c.execute("select infobox,sections from pages where slug='事件/赵活街头遇跪求药人'").fetchone()
print("\n事件 infobox:", e[0])
print("sections:", [s["h"] for s in json.loads(e[1])])
for s in json.loads(e[1]):
    if s["h"] == "时间推导":
        print("推导:", s["html"][:220])

print("\n人物总数", c.execute("select count(*) from pages where type='人物'").fetchone()[0])
