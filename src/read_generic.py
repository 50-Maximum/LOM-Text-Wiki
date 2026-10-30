# -*- coding: utf-8 -*-
"""读 5 个泛标题场景全文，准备人工命名。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row
for sc in ["S0014_01_01", "S0213_02", "S0502_01", "S2914_02", "S2901_03_01_06_02"]:
    r = con.execute("select title,chapter,line_count from scenes where script=?", (sc,)).fetchone()
    print("\n===== %s %s（%s，%s句）" % (sc, r["title"], r["chapter"], r["line_count"]))
    for x in con.execute("select seq,text,speaker from lines where script=? order by seq", (sc,)):
        print("  #%d [%s] %s" % (x["seq"], x["speaker"], (x["text"] or "").replace("\n", " ")[:100]))
