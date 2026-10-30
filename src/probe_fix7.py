# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

def evs(script):
    print(f"\n===== {script} 事件 =====")
    for r in c.execute("select name,substr(note,1,42) from notes where script=? and type='事件'", (script,)):
        print(f"  [{r[0]}] {r[1]}")

def lines(kw, limit=8):
    print(f"\n===== lines {kw} =====")
    for r in c.execute("select script,seq,speaker,replace(substr(text,1,80),char(10),'/') from lines where text like ? limit ?", (f"%{kw}%", limit)):
        print(f"{r[0]}#{r[1]} [{r[2]}] {r[3]}")

evs("ch3_11_2")
evs("S9906_01_02")
evs("S0018_03")
evs("ch0_meeting_option_02")
lines("卧云岗", 10)
evs("ch4_5_1")
