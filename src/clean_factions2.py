# -*- coding: utf-8 -*-
"""修正门派数据：删文本碎片、废掉「活动地点」推断、归一名变体。"""
import sqlite3, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)
c.execute("PRAGMA journal_mode=WAL")

GARBAGE = ["一时半会", "没想到会", "背有靠山", "当然会", "迟早会",
           "与唐门", "可是唐门", "在唐门", "对唐门", "是唐门", "晚辈唐门",
           "至于本门", "都说唐门", "如今本门", "与本门"]
for g in GARBAGE:
    c.execute("delete from factions where name=?", (g,))
    c.execute("delete from char_faction where faction=?", (g,))
print("删碎片势力", len(GARBAGE))

# 活动地点推断全部废除（在地点出现 ≠ 属于该门派）
n = c.execute("select count(*) from char_faction where method='活动地点'").fetchone()[0]
c.execute("delete from char_faction where method='活动地点'")
print("废除活动地点推断", n, "条")

# 同人多 id：按名字合并，保留最强证据
rows = c.execute("""select cf.char_id, n.name, cf.faction, cf.score, cf.method
                    from char_faction cf join names n on n.id=cf.char_id""").fetchall()
best = {}
rank = {"自称": 3, "名字": 2, "姓氏": 1}
for cid, name, fac, score, method in rows:
    key = name
    cur = best.get(key)
    if not cur or rank.get(method, 0) > rank.get(cur[3], 0):
        best[key] = (cid, fac, score, method)
c.execute("delete from char_faction")
for name, (cid, fac, score, method) in best.items():
    c.execute("insert or replace into char_faction(char_id,faction,score,method) values(?,?,?,?)",
              (cid, fac, score, method))
print("按人名合并后归属", len(best), "人")

c.commit()
print()
print("势力数", c.execute("select count(*) from factions").fetchone()[0])
for r in c.execute("""select f.name,f.kind,count(cf.char_id) n from factions f
                      left join char_faction cf on cf.faction=f.name
                      group by f.name order by n desc, f.name"""):
    print(f"   {r[0]:<12} {r[1] or '':<4} {r[2]}")
