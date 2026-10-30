# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

def scene(script, lo=None, hi=None):
    print(f"\n===== {script} =====")
    rows = c.execute("select seq,speaker,replace(text,char(10),'⏎') from lines where script=? order by seq", (script,)).fetchall()
    if lo is not None:
        rows = [r for r in rows if r[0] >= lo and (hi is None or r[0] <= hi)]
    for r in rows:
        print(f"{r[0]} [{r[1]}] {r[2][:110]}")

scene("ch8_1_1_2_2_1")          # 唐升之死
scene("S0204_01_01_01", 1, 60)  # 叶云舟辞行
