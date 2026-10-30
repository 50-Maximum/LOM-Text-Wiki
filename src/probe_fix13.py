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

evs("S0208_02_03")
evs("ch2_4_5_1")
evs("ch2_2_5_4")
evs("ch3_1_4_1")
evs("S3001_01")
lines("金背龙王刀", 5)
lines("山贼", 8)
lines("飞石", 10)
lines("福韫", 12)
lines("无相", 8)
