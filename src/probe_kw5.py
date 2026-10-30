# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

def notes(kw, limit=25):
    print(f"\n===== notes {kw} =====")
    for r in c.execute("""select script,seq_from,name,note,quote from notes
                          where name like ? or note like ? order by script,seq_from limit ?""",
                       (f"%{kw}%", f"%{kw}%", limit)):
        print(f"{r[0]}#{r[1]} [{r[2]}] {r[3][:62]} | {r[4][:36]}")

def lines(kw, limit=20, scripts=None):
    print(f"\n===== lines {kw} =====")
    q = "select script,seq,speaker,replace(substr(text,1,70),char(10),'/') from lines where text like ?"
    args = [f"%{kw}%"]
    if scripts:
        q += " and script like ?"
        args.append(scripts)
    q += " limit ?"
    args.append(limit)
    for r in c.execute(q, args):
        print(f"{r[0]}#{r[1]} [{r[2]}] {r[3]}")

notes("唐中翎")
notes("唐升死")
lines("云舟", 25, "ch8_8_1%")
lines("云裳", 25, "ch8_8_1%")
notes("唐门掌门", 12)
notes("新掌门", 12)
