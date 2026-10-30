# -*- coding: utf-8 -*-
"""查山村野店出现的场景与上下文，判断它到底在哪。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
hit = set()
for r in c.execute("select script,seq,speaker,text from lines where text like '%野店%'"):
    hit.add(r["script"])
for r in c.execute("select script,seq,speaker,text from lines where text like '%山村%'"):
    hit.add(r["script"])
print("涉及脚本:", len(hit))
for sc in sorted(hit):
    d = c.execute("select title,chapter,place from scenes where script=?", (sc,)).fetchone()
    print("\n== %s | %s | %s | place=%s" % (sc, d["title"], d["chapter"], d["place"]))
    n = 0
    for r in c.execute("select seq,speaker,text from lines where script=? order by seq", (sc,)):
        t = r["text"] or ""
        if ("野店" in t or "山村" in t or "客栈" in t or "客店" in t) and n < 8:
            print("   #%d %s %s" % (r["seq"], (r["speaker"] or "")[:8], t[:100]))
            n += 1
