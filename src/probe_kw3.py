# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

def notes(kw, limit=25, where="name like ?"):
    print(f"\n===== notes {kw} =====")
    for r in c.execute(f"""select script,seq_from,name,note,quote from notes
                           where {where} order by script,seq_from limit ?""", (f"%{kw}%", limit)):
        print(f"{r[0]}#{r[1]} [{r[2]}] {r[3][:60]} | {r[4][:40]}")

notes("叶云裳", 40)
notes("南宫深", 15)
notes("唐中翎", 15)
notes("掌门", 20, "note like ? and (note like '%唐门%' or name like '%唐%')")
notes("西武林盟胜", 12)
