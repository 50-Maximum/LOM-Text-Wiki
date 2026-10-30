# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print(c.execute("select title,place from scenes where script='ch8_6_3'").fetchone())
for s, sp, t in c.execute("select seq,speaker,text from lines where script='ch8_6_3' and seq between 118 and 133 order by seq"):
    print(" %4d %-8s %s" % (s, (sp or "")[:8], (t or "").replace("\n", " ")[:120]))
