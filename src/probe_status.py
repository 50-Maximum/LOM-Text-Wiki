# -*- coding: utf-8 -*-
import sqlite3, os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
print("notes:", c.execute("select count(*) from notes").fetchone()[0],
      "条 /", c.execute("select count(distinct script) from notes").fetchone()[0], "场景")
has = c.execute("select count(*) from sqlite_master where name='routes'").fetchone()[0]
if has:
    rows = c.execute("select flag,name,substr(summary,1,80),exclusive from routes").fetchall()
    print("routes:", len(rows))
    for r in rows:
        print("  ", r[0], "|", r[1], "|", r[2], "|", r[3])
else:
    print("routes: 表未建")
