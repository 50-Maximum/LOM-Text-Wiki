# -*- coding: utf-8 -*-
"""查 O_xxx 选项键的中文出处 + choices 覆盖情况。"""
import os, sys, io, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))

print("== choices 总量 ==", c.execute("select count(*) from choices").fetchone()[0])
print("== 含 O_ 键的行 ==")
rows = c.execute("select script,seq,checkpoint,options from choices where options like '%O\\_%' escape '\\' limit 6").fetchall()
print("  行数", c.execute("select count(*) from choices where options like '%O\\_%' escape '\\'").fetchone()[0])
for s, q, cp, o in rows:
    print(f"\n  {s} seq{q} cp={cp}")
    for it in json.loads(o)[:4]:
        print("    ", it)

print("\n== kv 表结构 ==")
for r in c.execute("PRAGMA table_info(kv)"):
    print("  ", r)
print("  样本:", c.execute("select * from kv limit 3").fetchall())

t = json.load(open(os.path.join(BASE, "data", "build", "text.json"), encoding="utf-8"))
print("\n== text.json O_ 样本 ==")
for k in ["O_8_2_5_8_1_001", "O_5_6_8_3_4_001"]:
    print("  ", k, "=>", t.get(k))
