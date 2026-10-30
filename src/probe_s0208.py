# -*- coding: utf-8 -*-
"""S0208_05_05：病根得除与幽泉附身，是不是两条分支。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
t = c.execute("select title from scenes where script='S0208_05_05'").fetchone()
print("场景:", t[0] if t else "-")
for seq, sp, tx in c.execute("""select seq,speaker,text from lines where script='S0208_05_05'
                                order by seq limit 60"""):
    print("  %-4s %-8s %s" % (seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:82]))
