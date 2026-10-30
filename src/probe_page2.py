# -*- coding: utf-8 -*-
import sqlite3, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
r = c.execute("select name, lead, length(sections), substr(sections,1,150) from pages where slug='人物/赵活'").fetchone()
print(r)
print("---- 页面类型计数 ----")
for x in c.execute("select type,count(*) from pages group by type order by 2 desc"):
    print(x)
print("---- 场景 ch5_3_1 ----")
r2 = c.execute("select name, length(sections), substr(sections,1,200) from pages where slug='场景/ch5_3_1'").fetchone()
print(r2)
