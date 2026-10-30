# -*- coding: utf-8 -*-
import sqlite3, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== 姓氏法归属 ==")
for r in c.execute("""select cf.faction,n.name,cf.score from char_faction cf
                      left join names n on n.id=cf.char_id
                      where cf.method='姓氏' order by cf.faction"""):
    print(f"   {r[0]:<10} {r[1]}")

print()
print("== 自称法归属 ==")
for r in c.execute("""select cf.faction,n.name from char_faction cf
                      left join names n on n.id=cf.char_id
                      where cf.method='自称' order by cf.faction"""):
    print(f"   {r[0]:<10} {r[1]}")

print()
print("== 活动地点法：人数最多的门派 ==")
for r in c.execute("""select faction,count(*) from char_faction where method='活动地点'
                      group by faction order by 2 desc limit 25"""):
    print(f"   {r[0]:<12} {r[1]}")

print()
print("== 活动地点法样本人名（前 30）==")
for r in c.execute("""select cf.faction,n.name from char_faction cf
                      left join names n on n.id=cf.char_id
                      where cf.method='活动地点' limit 30"""):
    print(f"   {r[0]:<10} {r[1]}")
