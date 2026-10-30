# -*- coding: utf-8 -*-
"""逐个确认候选场景是不是「整场是梦」：看开头几句的叙述框架。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for sc in ("ch1_2_4", "ch5_4_8_6", "ch4_9_3_2", "ch3_1_4_1", "S0208_04_01_07", "ch8_7_2_1"):
    t = c.execute("select title from scenes where script=?", (sc,)).fetchone()
    print("\n=== %s ｜ %s" % (sc, (t[0] if t else "")[:30]))
    for seq, sp, tx in c.execute("""select seq,speaker,text from lines where script=?
                                    order by seq limit 8""", (sc,)):
        print("  %-4s %-8s %s" % (seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:74]))
