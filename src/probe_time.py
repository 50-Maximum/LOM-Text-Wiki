# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
print("title_src:", c.execute("select title_src,count(*) from scenes group by title_src").fetchall())
print("time_from 非空:", c.execute("select count(*) from scenes where time_from<>''").fetchone()[0])
print("time_to 非空:", c.execute("select count(*) from scenes where time_to<>''").fetchone()[0])
print("tkey>0:", c.execute("select count(*) from scenes where tkey>0").fetchone()[0])
print("样例：")
for r in c.execute("select script,title,title_src,time_from,time_to from scenes where time_from<>'' limit 6"):
    print("   ", r)
