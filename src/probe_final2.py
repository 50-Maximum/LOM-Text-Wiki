# -*- coding: utf-8 -*-
"""看终章 ch8_8_1 的分支结构（结局分流）。"""
import os, sys, io, sqlite3, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== ch8_8_1 的抉择/条件点 ==")
for r in c.execute("""select seq,kind,idx,text,cond,ctx,n_lines,flags,scenes
                      from branch_nodes where script='ch8_8_1' order by seq,idx"""):
    print(f"  seq{r[0]} [{r[1]}#{r[2]}] {r[3][:36]}｜cond={r[4][:24]}｜句{r[6]}")
    if r[5]:
        print(f"       ctx: {r[5][:110]}")
    if r[7] != "[]":
        print(f"       flags: {r[7][:90]}")

print("\n== ch8_8_1 里所有 SetFlag ==")
for r in c.execute("select seq,flag,value,branch from flags where script='ch8_8_1' order by seq"):
    print(f"  seq{r[0]} {r[1]}={r[2]}  {r[3][:80]}")

print("\n== ch8_8_1 分支标签分布 ==")
cnt = collections.Counter()
for (b,) in c.execute("select branch from lines where script='ch8_8_1' and branch<>''"):
    cnt[b.split(" > ")[-1][:40]] += 1
for k, v in cnt.most_common(12):
    print(f"  {v:4}  {k}")
