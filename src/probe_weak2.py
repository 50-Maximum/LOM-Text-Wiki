# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
for src in ("weak", "derived", None):
    q = "select script,title,chapter,line_count from scenes where title_src is null" if src is None \
        else "select script,title,chapter,line_count from scenes where title_src=?"
    args = () if src is None else (src,)
    rows = c.execute(q + " order by line_count desc limit 12", args).fetchall()
    print("==", src, "共", c.execute(
        "select count(*) from scenes where title_src is null" if src is None
        else "select count(*) from scenes where title_src=?", args).fetchone()[0], "==")
    for r in rows:
        print(f"   {r[0]:<30} {r[1][:40] if r[1] else '（空）'}  [{r[2]}] {r[3]}句")
    print()
