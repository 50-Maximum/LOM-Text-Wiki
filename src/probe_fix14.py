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
    for r in c.execute("select script,seq,speaker,replace(substr(text,1,90),char(10),'/') from lines where text like ? limit ?", (f"%{kw}%", limit)):
        print(f"{r[0]}#{r[1]} [{r[2]}] {r[3]}")

evs("S2200_04_01")
evs("ch2_2_6_2")
evs("ch8_4_3_2")
evs("S0703_01_01")
lines("雪山", 10)
lines("洞庭", 6)
lines("交换武学", 4)
lines("九转轮回", 6)
