# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
print([r[1] for r in c.execute("pragma table_info(scenes)")])
print()
print("标题来源分布：")
for r in c.execute("select title_src,count(*) from scenes group by title_src order by 2 desc"):
    print("   ", r)
print()
print("弱名样例：")
for r in c.execute("select script,title,chapter from scenes where title_src='弱名' limit 20"):
    print(f"   {r[0]:<28} {r[1]}  [{r[2]}]")
