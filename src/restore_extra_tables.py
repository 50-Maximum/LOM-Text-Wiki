# -*- coding: utf-8 -*-
"""从备份库补回非解析类表（台账/实体/势力归属/笔记/路线/结局/时间序等）。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
NEW = r"D:\LegendOfMortal Wiki\data\wiki.db"
OLD = r"D:\LegendOfMortal Wiki\data\wiki.db.bak_before_6001"

COPY = ["ledger", "entities", "char_faction", "notes", "routes", "endings",
        "scene_order", "guide_events", "guide_index", "scene_time"]

con = sqlite3.connect(NEW)
con.execute("ATTACH DATABASE ? AS bak", (OLD,))
have = {r[0] for r in con.execute("select name from sqlite_master where type='table'")}
for t in COPY:
    ex = con.execute("select count(*) from bak.sqlite_master where type='table' and name=?",
                     (t,)).fetchone()[0]
    if not ex:
        print("备份无此表:", t)
        continue
    if t in have:
        con.execute('DROP TABLE "%s"' % t)
    con.execute('CREATE TABLE "%s" AS SELECT * FROM bak."%s"' % (t, t))
    n = con.execute('select count(*) from "%s"' % t).fetchone()[0]
    print("已补 %-14s %d 行" % (t, n))
con.commit()
con.execute("DETACH DATABASE bak")
con.close()
print("完成")
