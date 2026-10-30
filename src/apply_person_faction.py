# -*- coding: utf-8 -*-
"""把审查过的人物归属写回实体表与 char_faction。"""
import sqlite3, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)
c.execute("PRAGMA journal_mode=WAL")

res = json.load(open(r"D:\LegendOfMortal Wiki\data\person_faction.json", encoding="utf-8"))
cols = [r[1] for r in c.execute("pragma table_info(entities)")]
if "faction" not in cols:
    c.execute("alter table entities add column faction TEXT default ''")
if "faction_ev" not in cols:
    c.execute("alter table entities add column faction_ev TEXT default ''")

fac_names = {r[0] for r in c.execute("select name from factions")}
bad, ok = [], 0
for name, (fac, ev) in res.items():
    if fac and fac not in fac_names:
        bad.append((name, fac))
        continue
    c.execute("update entities set faction=?, faction_ev=? where type='人物' and name=?",
              (fac, ev, name))
    if fac:
        ok += 1
print("写入归属", ok, "人；非法势力名", len(bad))
for b in bad[:20]:
    print("   ?", b)

# char_faction 以审查结果为准重建（只保留有明确证据的）
c.execute("delete from char_faction")
rows = c.execute("select name,faction from entities where type='人物' and faction<>''").fetchall()
n = 0
for name, fac in rows:
    ids = [r[0] for r in c.execute("select id from names where name=?", (name,))]
    for cid in ids:
        c.execute("insert or replace into char_faction(char_id,faction,score,method) values(?,?,?,?)",
                  (cid, fac, 9, "审查"))
        n += 1
c.commit()
print("char_faction", n, "条")

print()
print("== 归属分布 ==")
for r in c.execute("""select faction,count(*) from entities where type='人物' and faction<>''
                      group by faction order by 2 desc"""):
    print(f"   {r[0]:<10} {r[1]}")
print()
print("无归属人物", c.execute("select count(*) from entities where type='人物' and (faction='' or faction is null)").fetchone()[0])
