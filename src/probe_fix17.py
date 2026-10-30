# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

def scene(script, lo=None, hi=None, cap=30, kw=None):
    print(f"\n===== {script} =====")
    rows = c.execute("select seq,speaker,replace(text,char(10),'⏎') from lines where script=? order by seq", (script,)).fetchall()
    if lo is not None:
        rows = [r for r in rows if r[0] >= lo and (hi is None or r[0] <= hi)]
    if kw:
        rows = [r for r in rows if kw in r[2]]
    for r in rows[:cap]:
        print(f"{r[0]} [{r[1]}] {r[2][:95]}")

scene("ch7_5_2_2", kw="魏菊")
scene("ch7_6_1", kw="孟")
scene("ch6_9_2", kw="孟仙谣")
