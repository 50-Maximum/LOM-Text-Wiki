# -*- coding: utf-8 -*-
import os, sys, io, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
print("notes", c.execute("select count(*) from notes").fetchone()[0],
      "场景", c.execute("select count(distinct script) from notes").fetchone()[0])
print("branches 表结构")
for r in c.execute("PRAGMA table_info(branches)"):
    print("  ", r)
print("  条数", c.execute("select count(*) from branches").fetchone()[0])
for r in c.execute("select * from branches limit 3"):
    print("  ", r)
print("\nroutes", c.execute("select count(*) from routes").fetchone()[0])
print("\nnotes 表结构")
for r in c.execute("PRAGMA table_info(notes)"):
    print("  ", r)
