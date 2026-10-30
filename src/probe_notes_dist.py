# -*- coding: utf-8 -*-
"""看 notes 的类型与名字分布，决定归并规则。"""
import os, sys, io, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== 类型分布 ==")
for r in c.execute("select type,count(*),count(distinct name) from notes group by type order by 2 desc"):
    print(f"  {r[0]:8} 条 {r[1]:6}  名字 {r[2]}")

print("\n== 人物 top 40 ==")
for r in c.execute("""select name,count(*) from notes where type='人物'
                      group by name order by 2 desc limit 40"""):
    print(f"  {r[0]:10} {r[1]}")

print("\n== 势力 top 25 ==")
for r in c.execute("""select name,count(*) from notes where type='势力'
                      group by name order by 2 desc limit 25"""):
    print(f"  {r[0]:14} {r[1]}")

print("\n== 地点 top 20 ==")
for r in c.execute("""select name,count(*) from notes where type='地点'
                      group by name order by 2 desc limit 20"""):
    print(f"  {r[0]:14} {r[1]}")

print("\n== 事件样例 10 ==")
for r in c.execute("select name,note,quote from notes where type='事件' limit 10"):
    print(f"  {r[0]}｜{r[1]}")

print("\n== 书物样例 8 ==")
for r in c.execute("select name,note from notes where type='书物' limit 8"):
    print(f"  {r[0]}｜{r[1]}")
