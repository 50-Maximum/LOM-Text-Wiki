# -*- coding: utf-8 -*-
"""备份 / 恢复 scenes.title（重建库会丢事件名）。用法: python titles_backup.py save|load"""
import sqlite3, sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
BAK = r"D:\LegendOfMortal Wiki\data\titles_backup.json"
mode = sys.argv[1] if len(sys.argv) > 1 else "save"
c = sqlite3.connect(DB)
c.execute("PRAGMA journal_mode=WAL")

if mode == "save":
    rows = c.execute("select script,title,title_src from scenes where title<>'' and title is not null").fetchall()
    json.dump(rows, open(BAK, "w", encoding="utf-8"), ensure_ascii=False)
    print("备份", len(rows), "条标题 →", BAK)
else:
    cols = [r[1] for r in c.execute("pragma table_info(scenes)")]
    if "title_src" not in cols:
        c.execute("alter table scenes add column title_src TEXT")
    if "title" not in cols:
        c.execute("alter table scenes add column title TEXT")
    rows = json.load(open(BAK, encoding="utf-8"))
    c.executemany("update scenes set title=?, title_src=? where script=?", rows)
    c.commit()
    print("恢复", len(rows), "条标题")
