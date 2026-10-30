# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
for p in (r"D:\LegendOfMortal Wiki\data\wiki.db", r"D:\LegendOfMortal Wiki\dist\活侠传Wiki\data\wiki.db"):
    c = sqlite3.connect("file:" + p.replace("\\", "/") + "?mode=ro", uri=True).cursor()
    print(p)
    print("   pages:", c.execute("select count(*) from pages").fetchone()[0],
          " links:", c.execute("select count(*) from links").fetchone()[0],
          " 地图事件:", c.execute("select count(*) from pages where slug like '地图事件/%'").fetchone()[0])
