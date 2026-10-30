# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

def lines(kw, limit=12):
    print(f"\n===== lines {kw} =====")
    for r in c.execute("select script,seq,speaker,replace(substr(text,1,95),char(10),'/') from lines where text like ? limit ?", (f"%{kw}%", limit)):
        print(f"{r[0]}#{r[1]} [{r[2]}] {r[3]}")

lines("割下了掌派人", 5)
lines("踢飞", 6)
lines("金乌上人", 18)
lines("拜师", 10)
lines("唐中翎", 14)
lines("南溪", 10)
lines("结缘", 10)
lines("瑞笙", 14)
