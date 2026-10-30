# -*- coding: utf-8 -*-
import sqlite3, collections, re

c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
print("total", c.execute("select count(*) from ledger").fetchone()[0])
print("uniq type+name",
      c.execute("select count(*) from (select distinct type,name from ledger)").fetchone()[0])
print()
print("-- 同一条目重复次数最多的 --")
for r in c.execute("select type,name,count(*) n from ledger group by type,name order by n desc limit 20"):
    print(f"  {r[0]:<4} {r[1]:<22} x{r[2]}")
print()
print("-- 人物名过长（可能是句子）--")
for r in c.execute("select name,count(*) from ledger where type='人物' and length(name)>7 group by name order by 2 desc limit 20"):
    print(f"  {r[0]}  x{r[1]}")
print()
print("-- 疑似泛称 --")
GEN = ("弟子", "众人", "那人", "此人", "有人", "旁人", "少年", "少女", "老者", "汉子",
       "掌柜", "小二", "村民", "百姓", "士兵", "江湖人", "黑衣人", "陌生人", "路人")
for r in c.execute("select type,name,count(*) from ledger group by type,name"):
    if r[1] in GEN or any(r[1].endswith(g) and len(r[1]) <= 5 for g in GEN):
        print(f"  {r[0]:<4} {r[1]:<14} x{r[2]}")
print()
print("-- 各章条数 --")
for r in c.execute("select chapter,count(*) from ledger group by chapter order by 1"):
    print(f"  {r[0]:<12} {r[1]}")
