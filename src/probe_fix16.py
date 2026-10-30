# -*- coding: utf-8 -*-
import sqlite3, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

def lines(kw, limit=10, scripts=None):
    print(f"\n===== lines {kw} =====")
    q = "select script,seq,speaker,replace(substr(text,1,80),char(10),'/') from lines where text like ?"
    args = [f"%{kw}%"]
    if scripts:
        q += " and script like ?"; args.append(scripts)
    q += " limit ?"; args.append(limit)
    for r in c.execute(q, args):
        print(f"{r[0]}#{r[1]} [{r[2]}] {r[3]}")

def evs(script):
    print(f"\n===== {script} 事件 =====")
    for r in c.execute("select name,substr(note,1,42) from notes where script=? and type='事件'", (script,)):
        print(f"  [{r[0]}] {r[1]}")

lines("烧菜", 6)
lines("续写唐门史", 5)
lines("没曾后悔", 5)
lines("小菊跟了你", 5)
lines("跟魏掌门学读书", 5)
