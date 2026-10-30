# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
print("== factions 60 ==")
for r in c.execute("select kind,name from factions order by kind,name"):
    print(f"   {r[0]:<4} {r[1]}")
print()
print("== 势力实体（70）==")
print("、".join(r[0] for r in c.execute("select name from entities where type='势力' order by mentions desc")))
