# -*- coding: utf-8 -*-
import sqlite3, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
r = c.execute("select infobox,sections from pages where slug='地点/眉山'").fetchone()
print("眉山 infobox", r[0])
print("眉山下辖", [x["note"][:20] for s in json.loads(r[1]) if s["h"] == "下辖地点" for x in s["rows"]])
e = c.execute("select infobox,sections from pages where slug='事件/武林盟围攻唐门血战'").fetchone()
print("事件 infobox", e[0])
print("事件 sections", [s["h"] for s in json.loads(e[1])])
print("顶层地点数", c.execute("select count(*) from pages where type='地点' and slug not in (select slug from place_children)").fetchone()[0])
