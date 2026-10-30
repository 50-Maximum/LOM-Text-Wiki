# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

def lines(kw, limit=8):
    print(f"\n===== lines {kw} =====")
    for r in c.execute("select script,seq,speaker,replace(substr(text,1,90),char(10),'/') from lines where text like ? limit ?", (f"%{kw}%", limit)):
        print(f"{r[0]}#{r[1]} [{r[2]}] {r[3]}")

lines("千灯楼", 10)
lines("烧香", 6)
def scene(script, lo=None, hi=None, cap=20):
    print(f"\n===== {script} =====")
    rows = c.execute("select seq,speaker,replace(text,char(10),'⏎') from lines where script=? order by seq", (script,)).fetchall()
    if lo is not None:
        rows = [r for r in rows if r[0] >= lo and (hi is None or r[0] <= hi)]
    for r in rows[:cap]:
        print(f"{r[0]} [{r[1]}] {r[2][:95]}")
scene("ch8_2_5_6", 1, 25)
