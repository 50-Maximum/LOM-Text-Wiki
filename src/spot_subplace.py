# -*- coding: utf-8 -*-
"""抽查正文地名判定的高风险条目。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row
for sc in ["S0022_01", "S0024_01_03", "S0018_01", "S0021_01", "S0024_01"]:
    r = con.execute("select title from scenes where script=?", (sc,)).fetchone()
    print("\n== %s %s" % (sc, (r["title"] if r else "") or ""))
    for x in con.execute("select seq,text,speaker from lines where script=? order by seq limit 4", (sc,)):
        print("   #%d [%s] %s" % (x["seq"], x["speaker"], (x["text"] or "").replace("\n", " ")[:70]))
