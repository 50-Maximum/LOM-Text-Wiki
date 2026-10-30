# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

for nm in ("向无忧", "唐铮"):
    print(f"\n== {nm} 关键笔记 ==")
    for r in c.execute("""select script,note,quote from notes where name=?
                          and (note like '%掌门%' or note like '%叛%' or note like '%魔教%'
                               or note like '%峨嵋%' or note like '%毒%' or note like '%掌门%')
                          limit 10""", (nm,)):
        print("  ", r[0], "|", r[1][:60], "|", (r[2] or "")[:30])
