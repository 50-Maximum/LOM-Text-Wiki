# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
for r in c.execute("select slug,name from pages where type='事件' and (name like '%求药%' or name like '%斗笠%')"):
    print(r)
print("---- 场景 S0003_01_01 ----")
for r in c.execute("select script,title,place,chapter from scenes where script='S0003_01_01'"):
    print(r)
