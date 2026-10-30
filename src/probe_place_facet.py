# -*- coding: utf-8 -*-
import io, sys, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("地点页总数", c.execute("select count(*) from pages where type='地点'").fetchone()[0])
print("hidden=0", c.execute("select count(*) from pages where type='地点' and hidden=0").fetchone()[0])
for f, n in c.execute("""select coalesce(facet,'') , count(*) from pages
                         where type='地点' group by 1 order by 2 desc limit 12"""):
    print("  facet=%-10s %d" % (f or "（空）", n))
print("\n顶层 页面名：")
print("、".join(r[0] for r in c.execute("""select name from pages where type='地点' and facet='顶层'
                                          order by name""")))
