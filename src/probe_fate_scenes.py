# -*- coding: utf-8 -*-
"""打印关键命运旗标的设置场景与原文上下文。"""
import os, sys, io, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

FLAGS = ["M60026", "M10011", "M50018", "M40059", "E14001", "E14002", "E14003",
         "E13008", "E13009", "E13010", "M80084", "M80042", "M60077"]

for f in FLAGS:
    print(f"\n===== {f}")
    lab = c.execute("select label from flaginfo where flag=?", (f,)).fetchone()
    print("  标签:", lab[0] if lab else "无")
    for sc, sq, v, br in c.execute("select script,seq,value,branch from flags where flag=? order by script", (f,)).fetchall():
        t = c.execute("select title,chapter from scenes where script=?", (sc,)).fetchone()
        print(f"  设置于 {sc} seq{sq} = {v} 《{t[0] if t else ''}》")
        if br:
            print(f"     分支条件: {br[:110]}")
        for r in c.execute("select seq,speaker,text from lines where script=? and seq between ? and ? order by seq",
                           (sc, max(0, sq - 4), sq + 3)):
            print(f"       {r[0]:3} {r[1]}：{(r[2] or '').replace(chr(10),' ')[:80]}")
