# -*- coding: utf-8 -*-
"""看 ch2_2_3_1 到底在哪：取前后场与正文首尾。"""
import io, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "scripts")
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row
sc = "ch2_2_3_1"
r = c.execute("select title,chapter,line_count from scenes where script=?", (sc,)).fetchone()
print("场景:", r["title"], r["chapter"], r["line_count"], "句")
ls = list(c.execute("select seq,speaker,text from lines where script=? order by seq limit 8", (sc,)))
for x in ls:
    print("   [%d] %s：%s" % (x["seq"], x["speaker"] or "-", x["text"][:80]))
print("\n后 4 句:")
for x in c.execute("select seq,speaker,text from lines where script=? order by seq desc limit 4", (sc,)):
    print("   [%d] %s：%s" % (x["seq"], x["speaker"] or "-", x["text"][:80]))
print("\n入边:", [tuple(x) for x in c.execute("select src,type from scene_edges where dst=?", (sc,))][:6])
print("出边:", [tuple(x) for x in c.execute("select dst,type from scene_edges where src=?", (sc,))][:6])
