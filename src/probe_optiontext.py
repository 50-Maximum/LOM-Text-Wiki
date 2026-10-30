# -*- coding: utf-8 -*-
"""解析选项文本：O_ 键 ↔ kv 文本；并查看笔记进度。"""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

for k in ("O_5_6_8_3_4_001", "O_5_6_8_3_4_002", "O_5_6_8_3_5_001", "O_5_6_8_3_5_002"):
    rows = c.execute("select ns,value from kv where key=? limit 3", (k,)).fetchall()
    print(k, "→", rows)

print()
print("kv ns 列表：")
for r in c.execute("select ns,count(*) from kv group by ns order by 2 desc limit 10"):
    print("   ", r)

print()
print("notes 进度：", c.execute("select count(*) from notes").fetchone()[0],
      "条 /", c.execute("select count(distinct script) from notes").fetchone()[0], "场景")
