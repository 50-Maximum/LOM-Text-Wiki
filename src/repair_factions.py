# -*- coding: utf-8 -*-
"""修复：同名改类型时误删的势力行，按实体表重建 factions。"""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)
c.execute("PRAGMA journal_mode=WAL")

KIND = {"世家": "世家", "帮": "帮会", "教": "教派", "盟": "组织", "会": "组织",
        "宫": "势力", "阁": "势力", "楼": "势力", "门": "门派", "派": "门派"}

def guess(name):
    for k, v in KIND.items():
        if name.endswith(k):
            return v
    return "门派"

known = {r[0]: r[1] for r in c.execute("select name,kind from factions")}
rows = c.execute("select name from entities where type='势力'").fetchall()
added = 0
for (name,) in rows:
    if name in known:
        continue
    c.execute("insert into factions(name,kind,descr) values(?,?,?)",
              (name, known.get(name) or guess(name), "")) if False else None
    cols = [r[1] for r in c.execute("pragma table_info(factions)")]
    if "descr" in cols:
        c.execute("insert into factions(name,kind,descr) values(?,?,?)", (name, guess(name), ""))
    else:
        c.execute("insert into factions(name,kind) values(?,?)", (name, guess(name)))
    added += 1
    print("补回", name, guess(name))

c.commit()
print("factions", c.execute("select count(*) from factions").fetchone()[0])
for r in c.execute("""select f.name,f.kind,count(cf.char_id) n from factions f
                      left join char_faction cf on cf.faction=f.name
                      group by f.name order by n desc, f.name"""):
    print(f"   {r[0]:<12} {r[1] or '':<4} {r[2]}")
