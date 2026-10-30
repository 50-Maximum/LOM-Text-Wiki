# -*- coding: utf-8 -*-
"""给只有 1~2 条笔记的实体补简介（直接取笔记原文）。"""
import sqlite3, sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.execute("PRAGMA journal_mode=WAL")

rows = c.execute("select type,name from entities where intro=''").fetchall()
n = 0
for typ, name in rows:
    notes = [r[0].strip() for r in c.execute(
        "select note from ledger where type=? and name=? order by rowid", (typ, name))]
    seen, uniq = set(), []
    for x in notes:
        if x and x not in seen:
            seen.add(x); uniq.append(x)
    if not uniq:
        continue
    intro = uniq[0]
    for extra in uniq[1:3]:
        if extra not in intro:
            intro = intro.rstrip("。") + "。" + extra
    c.execute("update entities set intro=? where type=? and name=?", (intro[:400], typ, name))
    n += 1
c.commit()
print("补简介", n)
print("空简介剩", c.execute("select count(*) from entities where intro=''").fetchone()[0])
print("实体总数", c.execute("select count(*) from entities").fetchone()[0])
