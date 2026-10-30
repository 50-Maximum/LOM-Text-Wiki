# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
for r in c.execute("""select script,seq,speaker,substr(text,1,80) from lines
                      where text like '%鸡蛋%' and text like '%拜师%' limit 10"""):
    print(r)
