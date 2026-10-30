# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
rows = c.execute("select name,mentions from pages where type='势力' order by mentions desc").fetchall()
print("势力页", len(rows))
print(" / ".join(f"{n}({m})" for n, m in rows))
