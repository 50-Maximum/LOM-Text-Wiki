# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
for name in ("千灯楼", "南宫禹", "谭霸刀"):
    print("=" * 70)
    print(name)
    for r in c.execute("select chapter,type,note,evidence from ledger where name=? order by rowid limit 12", (name,)):
        print(f"  [{r[0]}] {r[2][:90]}")
        print(f"        «{r[3][:50]}»")
