# -*- coding: utf-8 -*-
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
for sc in ("S8300_01", "S8300_01_01", "alchemy_001", "ch1_1"):
    n = c.execute("select count(*) from lines where script=?", (sc,)).fetchone()[0]
    t = c.execute("select title from scenes where script=?", (sc,)).fetchone()
    print("\n### %-14s 台词 %3d 句 ｜ %s" % (sc, n, (t[0] if t else "?")))
    if sc in ("S8300_01", "S8300_01_01"):
        for seq, sp, tx in c.execute(
                "select seq,speaker,text from lines where script=? order by seq limit 8", (sc,)):
            print("   %-5s %-8s %s" % (seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:60]))
    if sc == "alchemy_001":
        for seq, sp, tx in c.execute(
                "select seq,speaker,text from lines where script=? order by seq limit 10", (sc,)):
            print("   %-5s %-8s %s" % (seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:60]))
