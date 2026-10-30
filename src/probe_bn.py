# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
for sc in ("ch5_3_1", "ch5_3_2", "ch5_3_3"):
    n1 = c.execute("select count(*) from branch_nodes where script=?", (sc,)).fetchone()[0]
    n2 = c.execute("select count(*) from notes where script=?", (sc,)).fetchone()[0]
    print(sc, "branch_nodes", n1, "notes", n2)
print("总 branch_nodes", c.execute("select count(*) from branch_nodes").fetchone()[0])
print("有分支表的场景", c.execute("select count(distinct script) from branch_nodes").fetchone()[0])
