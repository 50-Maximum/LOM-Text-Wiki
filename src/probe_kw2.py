# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
def hit(kw, limit=30):
    print(f"\n===== {kw} =====")
    for r in c.execute("""select script,seq,speaker,replace(text,char(10),'⏎') from lines
                          where text like ? limit ?""", (f"%{kw}%", limit)):
        print(f"{r[0]}#{r[1]} [{r[2]}] {r[3][:90]}")
hit("代掌门", 20)
hit("南宫深公子")
hit("说亲")
hit("提亲")
hit("外堡的租")
hit("租客")
hit("房租")
