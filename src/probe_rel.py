# -*- coding: utf-8 -*-
import sqlite3, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("-- 关系条目样例 --")
for r in c.execute("select name,note from ledger where type='关系' order by rowid limit 25"):
    print(f"  {r[0]}  ::  {r[1][:70]}")

print()
print("-- 提及次数分布 --")
for thr in (1, 2, 3, 5, 10):
    n = c.execute("select count(*) from (select name from ledger group by type,name having count(*)>=?)", (thr,)).fetchone()[0]
    print(f"  >={thr:>2} 次: {n} 个实体")

print()
print("-- 只有 1 次提及的随机 20 条（看是不是垃圾）--")
for r in c.execute("select type,name,note from ledger where (type,name) in (select type,name from ledger group by type,name having count(*)=1) order by random() limit 20"):
    print(f"  {r[0]:<3} {r[1]:<18} {r[2][:60]}")

print()
print("-- 完全重复的行数 --")
n = c.execute("select count(*) from ledger").fetchone()[0]
u = c.execute("select count(*) from (select distinct chapter,type,name,note from ledger)").fetchone()[0]
print(f"  {n} → 去重后 {u}")
