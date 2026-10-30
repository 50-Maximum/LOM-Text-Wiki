# -*- coding: utf-8 -*-
"""收尾修正：假归属清理 + 别名人物合并。"""
import sqlite3, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)
c.execute("PRAGMA journal_mode=WAL")

# 1) 证据只是「藏身/寄居/假扮」这类，不算归属
BAD = ("藏身", "隐居", "寄居", "假扮", "冒充", "伪装", "躲在", "投奔", "客居", "借宿")
rows = c.execute("select name,faction,faction_ev from entities "
                 "where type='人物' and faction<>''").fetchall()
cleared = []
for name, fac, ev in rows:
    if any(b in (ev or "") for b in BAD):
        c.execute("update entities set faction='', faction_ev='' where type='人物' and name=?",
                  (name,))
        cleared.append((name, fac, ev))
print("清除假归属", len(cleared))
for x in cleared:
    print("   ", x)

# 2) 别名人物并入正条
MERGE = {"阿鹤侠": "虞小梅", "本梅": "虞小梅", "梅夫人": "虞小梅", "鹤手": "虞小梅",
         "云裳": "叶云裳", "小梅": "虞小梅"}
for alias, main in MERGE.items():
    src = c.execute("select mentions from entities where type='人物' and name=?", (alias,)).fetchone()
    mainrow = c.execute("select aliases from entities where type='人物' and name=?", (main,)).fetchone()
    if not src or not mainrow:
        continue
    rows = c.execute("select rowid,chapter,note,evidence from ledger where type='人物' and name=?",
                     (alias,)).fetchall()
    for rid, ch, note, ev in rows:
        dup = c.execute("select 1 from ledger where chapter=? and type='人物' and name=? and note=?",
                        (ch, main, note)).fetchone()
        if dup:
            c.execute("delete from ledger where rowid=?", (rid,))
        else:
            c.execute("update ledger set name=? where rowid=?", (main, rid))
    try:
        al = json.loads(mainrow[0] or "[]")
    except Exception:
        al = []
    if alias not in al:
        al.append(alias)
    c.execute("update entities set aliases=?, mentions=(select count(*) from ledger "
              "where type='人物' and name=?) where type='人物' and name=?",
              (json.dumps(al, ensure_ascii=False), main, main))
    c.execute("delete from entities where type='人物' and name=?", (alias,))
    print(f"合并 {alias} → {main}，迁移 {len(rows)} 条")

c.commit()

# 3) 重建 char_faction（重建库时会被清掉）
c.execute("drop table if exists char_faction")
c.execute("create table char_faction(char_id TEXT PRIMARY KEY, faction TEXT, score INT, method TEXT)")
n = 0
for name, fac in c.execute("select name,faction from entities where type='人物' and faction<>''"):
    for (cid,) in c.execute("select id from names where name=?", (name,)):
        c.execute("insert or replace into char_faction values(?,?,?,?)", (cid, fac, 9, "审查"))
        n += 1
c.commit()
print("char_faction 重建", n, "条")

print()
print("人物实体", c.execute("select count(*) from entities where type='人物'").fetchone()[0])
print("有归属", c.execute("select count(*) from entities where type='人物' and faction<>''").fetchone()[0])
for n in ("龙渊", "虞小梅", "阿鹤侠"):
    r = c.execute("select faction,faction_ev from entities where type='人物' and name=?", (n,)).fetchone()
    print("   ", n, "→", r if r else "（已并入别名）")
