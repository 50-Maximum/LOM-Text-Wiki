# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
print("== 当前 势力 实体（85）==")
for r in c.execute("select name,mentions from entities where type='势力' order by mentions desc"):
    print(f"   {r[0]:<14} {r[1]}")
print()
print("== 当前 地点 实体数 ==", c.execute("select count(*) from entities where type='地点'").fetchone()[0])
