# -*- coding: utf-8 -*-
"""ch4_6_12/13 里有没有「赵活自白不舍唐门」；以及这两场为何被切成独立段。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

for sc in ("ch4_6_12", "ch4_6_13", "ch4_6_11"):
    t = c.execute("select title from scenes where script=?", (sc,)).fetchone()
    print("\n=== %s ｜ %s" % (sc, (t[0] if t else "-")))
    for seq, sp, tx in c.execute("""select seq,speaker,text from lines where script=?
        and (text like '%唐门%' or text like '%不舍%' or text like '%舍不%' or text like '%留恋%'
             or text like '%家%')
        order by seq limit 12""", (sc,)):
        print("  %-4s %-8s %s" % (seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:80]))
