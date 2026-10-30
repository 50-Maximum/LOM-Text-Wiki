# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

def lines(kw, limit=10, andkw=None):
    print(f"\n===== {kw} =====")
    q = "select script,seq,speaker,replace(substr(text,1,90),char(10),'/') from lines where text like ?"
    args = [f"%{kw}%"]
    if andkw:
        q += " and text like ?"; args.append(f"%{andkw}%")
    q += " limit ?"; args.append(limit)
    for r in c.execute(q, args):
        print(f"{r[0]}#{r[1]} [{r[2]}] {r[3]}")

lines("锦香宫", 12, "龙湘")
lines("经脉寸断", 6)
lines("独生千金", 4)
lines("唐三侠", 4)
lines("小师妹", 8, "唐中翎")
