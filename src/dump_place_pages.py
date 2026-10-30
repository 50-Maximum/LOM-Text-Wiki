# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
rows = c.execute("select name,mentions from pages where type='地点' order by mentions desc").fetchall()
print("地点页", len(rows))
line = []
for n, m in rows:
    line.append(f"{n}({m})")
print(" / ".join(line))
