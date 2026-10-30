# -*- coding: utf-8 -*-
import sqlite3, io, sys, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("===== 势力页全部 =====")
for (n,) in c.execute("select name from pages where type='势力' order by name"):
    print(n, end=" ｜ ")
print()

print("\n===== 含 龙/万里 的人物页 =====")
for (n,) in c.execute("select name from pages where type='人物' and (name like '%龙%' or name like '%万里%') order by name"):
    print(n, end=" ｜ ")
print()

print("\n===== 章节分布 =====")
for r in c.execute("select chapter,count(*) from scenes group by chapter order by 2 desc"):
    print(r)

print("\n===== 场景标题样本（按章） =====")
for ch in [x[0] for x in c.execute("select distinct chapter from scenes")]:
    rows = c.execute("select title from scenes where chapter=? order by script limit 6", (ch,)).fetchall()
    print(f"{ch}: " + "、".join(r[0] for r in rows))
