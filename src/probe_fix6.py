# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

def evs(script):
    print(f"\n===== {script} 事件 =====")
    for r in c.execute("select name,substr(note,1,45),substr(quote,1,26) from notes where script=? and type='事件'", (script,)):
        print(f"  [{r[0]}] {r[1]} | {r[2]}")

def lines(kw, limit=10):
    print(f"\n===== lines {kw} =====")
    for r in c.execute("select script,seq,speaker,replace(substr(text,1,80),char(10),'/') from lines where text like ? limit ?", (f"%{kw}%", limit)):
        print(f"{r[0]}#{r[1]} [{r[2]}] {r[3]}")

evs("ch0_6")
lines("通缉", 8)
lines("人间道法王", 8)
lines("大义分舵", 8)
lines("外堡租客", 5)
lines("房租", 5)
evs("ch2_2_3_4_3_break_01_04_02")
evs("ch2_8_2")
evs("S0024_01_02")
evs("ch7_3_2_7")
