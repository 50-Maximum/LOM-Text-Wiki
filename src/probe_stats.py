# -*- coding: utf-8 -*-
import sqlite3, os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)
print("ledger", c.execute("select count(*) from ledger").fetchone()[0])
print("entities", c.execute("select count(*) from entities").fetchone()[0])
print("有简介", c.execute("select count(*) from entities where length(intro)>0").fetchone()[0])
print("库大小", round(os.path.getsize(DB) / 1048576, 1), "MB")
print()
for t, n, m in c.execute("select type,count(*),sum(mentions) from entities group by type order by 2 desc"):
    print(f"  {t:<3} {n:>4} 个实体 / {m} 条提及")
