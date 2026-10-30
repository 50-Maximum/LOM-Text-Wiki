# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("title=Free 的场景:", c.execute("select count(*) from scenes where title='Free'").fetchone()[0])
for r in c.execute("select script,title,line_count,place from scenes where title='Free' limit 6"):
    print("   ", r)
print("\n场景名里含 free 的:", c.execute("select count(*) from scenes where script like '%free%' or title like '%free%'").fetchone()[0])
