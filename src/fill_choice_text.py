# -*- coding: utf-8 -*-
"""把 choices 表的选项键换成中文文本（来自 text.json 的 O_ 键）。

并补出选项所属场景的实际分支后果：同一脚本内 O_xxx 的序号、是否跳转场景。
"""
import os, sys, io, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
DB = os.path.join(BASE, "data", "wiki.db")

text = json.load(open(os.path.join(BASE, "data", "build", "text.json"), encoding="utf-8"))
c = sqlite3.connect(DB)
c.execute("PRAGMA journal_mode=WAL")

cols = [r[1] for r in c.execute("PRAGMA table_info(choices)")]
print("choices 列:", cols)
print("样例:", c.execute("select * from choices limit 3").fetchall())

hit = 0
miss = []
for cid, script, key in c.execute("select rowid, script, key from choices").fetchall():
    t = text.get(key)
    if t:
        c.execute("update choices set text=? where rowid=?", (t.strip(), cid))
        hit += 1
    else:
        miss.append((script, key))
c.commit()
print("命中", hit, "缺失", len(miss))
for m in miss[:10]:
    print("  缺", m)
