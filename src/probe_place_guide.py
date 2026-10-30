# -*- coding: utf-8 -*-
"""看两处典型：①S0014_01_03 到底在哪 ②攻略里有没有「地点：」可直接用"""
import io, sys, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

print("=== S0014_01_03 前 30 句")
for seq, sp, tx in c.execute("""select seq,speaker,text from lines where script='S0014_01_03'
                                order by seq limit 30"""):
    print(" %3d %-8s %s" % (seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:90]))

print("\n=== guide_events 里有地点的条数")
print(" ", c.execute("select count(*) from guide_events where place<>''").fetchone()[0])
for r in c.execute("""select name,place from guide_events where place<>'' limit 8"""):
    print("  ", r)

print("\n=== guide_index body 里出现「地点：」的条数")
print(" ", c.execute("select count(*) from guide_index where body like '%地点%'").fetchone()[0])
for r in c.execute("""select name,substr(body,1,120) from guide_index
                      where body like '%地点%' limit 5"""):
    print("  ", r[0], "|", r[1].replace("\n", " "))
