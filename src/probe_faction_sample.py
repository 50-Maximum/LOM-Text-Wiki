# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("=== char_faction 抽样（按 score 降序 40 条）")
for nm, fc, sc, me in c.execute("""select n.name, cf.faction, cf.score, cf.method
        from char_faction cf join names n on n.id=cf.char_id
        order by cf.score desc limit 40"""):
    print("   %-10s %-8s %s %s" % (nm, fc, sc, me))
print("\n=== 归属分布")
for fc, n in c.execute("""select cf.faction, count(*) from char_faction cf
        where cf.faction<>'' group by 1 order by 2 desc"""):
    print("   %-10s %d" % (fc, n))
