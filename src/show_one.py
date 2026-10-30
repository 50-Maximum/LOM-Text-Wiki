# -*- coding: utf-8 -*-
"""看 S2901_04_02_break_start_01 全文，为重命名做准备。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row
sc = "S2901_04_02_break_start_01"
r = con.execute("select script,title,chapter,line_count,place from scenes where script=?", (sc,)).fetchone()
print("标题:", r["title"], "| 章:", r["chapter"], "| 句:", r["line_count"], "| 地点:", r["place"])
for x in con.execute("select seq,text,speaker from lines where script=? order by seq", (sc,)):
    print("#%d [%s] %s" % (x["seq"], x["speaker"], (x["text"] or "").replace("\n", " ")))
