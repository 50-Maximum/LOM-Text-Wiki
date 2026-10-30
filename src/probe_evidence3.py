# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

def lines(kw, limit=10, script_like=None):
    print(f"\n===== lines {kw} =====")
    q = "select script,seq,speaker,replace(substr(text,1,95),char(10),'/') from lines where text like ?"
    args = [f"%{kw}%"]
    if script_like:
        q += " and script like ?"; args.append(script_like)
    q += " limit ?"; args.append(limit)
    for r in c.execute(q, args):
        print(f"{r[0]}#{r[1]} [{r[2]}] {r[3]}")

lines("拜入唐门", 8)
lines("叶云舟", 12)
lines("收为弟子", 8)
lines("六位夫人", 5)
lines("夫人", 10, "ch6_5_2%")
lines("夏灵犀", 8)
lines("瑞笙", 10, "ch6_5_2%")
lines("虞小梅", 12)
lines("千面人魔", 12)
