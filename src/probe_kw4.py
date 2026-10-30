# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

def notes(kw, limit=30):
    print(f"\n===== notes {kw} =====")
    for r in c.execute("""select script,seq_from,name,note,quote from notes
                          where name like ? or note like ? order by script,seq_from limit ?""",
                       (f"%{kw}%", f"%{kw}%", limit)):
        print(f"{r[0]}#{r[1]} [{r[2]}] {r[3][:62]} | {r[4][:36]}")

notes("梁有诗", 25)
notes("叶云舟辞行")
notes("后会已然无期")
notes("云裳", 40)
notes("赵活接")
notes("接掌")
notes("代掌门", 15)
