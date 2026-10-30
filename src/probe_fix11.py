# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

def lines(kw, limit=10):
    print(f"\n===== lines {kw} =====")
    for r in c.execute("select script,seq,speaker,replace(substr(text,1,90),char(10),'/') from lines where text like ? limit ?", (f"%{kw}%", limit)):
        print(f"{r[0]}#{r[1]} [{r[2]}] {r[3]}")

lines("大仁分舵", 5)
lines("大智分舵", 5)
lines("千面人魔", 10)
lines("要求娶唐小娘子", 5)
lines("虞小梅", 8)
