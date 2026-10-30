# -*- coding: utf-8 -*-
import sqlite3, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("===== ch8_1_1_2 branch_nodes =====")
for r in c.execute("select seq,kind,idx,text,cond,flags,scenes from branch_nodes where script='ch8_1_1_2' order by seq,idx"):
    print(r)

print("\n===== ch8_1_1_2 场景行 =====")
for r in c.execute("select seq,speaker,replace(substr(text,1,70),char(10),'/') from lines where script='ch8_1_1_2' order by seq"):
    print(f"{r[0]} [{r[1]}] {r[2]}")

print("\n===== ch8_1_1_4 场景行 =====")
for r in c.execute("select seq,speaker,replace(substr(text,1,80),char(10),'/') from lines where script='ch8_1_1_4' order by seq limit 30"):
    print(f"{r[0]} [{r[1]}] {r[2]}")
