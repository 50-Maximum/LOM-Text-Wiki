# -*- coding: utf-8 -*-
import os, sys, io, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== meeting_option_01 ==")
for r in c.execute("select seq,idx,kind,text,flags from branch_nodes where script='meeting_option_01' order by seq,idx"):
    print("  ", r)

print("\n== ch3_3_1_1 ==")
for r in c.execute("select seq,idx,kind,text,flags from branch_nodes where script='ch3_3_1_1' order by seq,idx"):
    print("  ", r)

print("\n== 进度 ==", c.execute("select count(*) from notes").fetchone()[0], "条 /",
      c.execute("select count(distinct script) from notes").fetchone()[0], "场景")
print("routes", c.execute("select count(*) from routes").fetchone()[0])
print("branch_nodes", c.execute("select count(*) from branch_nodes").fetchone()[0])
