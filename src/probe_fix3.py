# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

def lines(kw, limit=12):
    print(f"\n===== lines {kw} =====")
    for r in c.execute("select script,seq,speaker,replace(substr(text,1,80),char(10),'/') from lines where text like ? limit ?", (f"%{kw}%", limit)):
        print(f"{r[0]}#{r[1]} [{r[2]}] {r[3]}")

def evs(script):
    print(f"\n===== {script} 事件 =====")
    for r in c.execute("select name,substr(note,1,45),substr(quote,1,26) from notes where script=? and type='事件'", (script,)):
        print(f"  [{r[0]}] {r[1]} | {r[2]}")

lines("毛二壮", 12)
evs("ch8_2_5_6")
evs("ch1_1_break_option")
evs("ch2_5_1")
evs("ch8_1_1_2_2_1")
evs("S0204_01_01_01")
evs("ch7_5_2_10")
evs("S0208_05_05")
