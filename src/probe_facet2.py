# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for t in ("事件", "场景", "剧情段"):
    print(t, c.execute("""select facet2,count(*) from pages where type=?
                          group by 1 order by 2 desc""", (t,)).fetchall())
print("\n样例（主线段）：")
for r in c.execute("""select slug,lead from pages where type='剧情段' and facet2='主线'
                      order by slug limit 3"""):
    print("  ", r[0], "|", r[1][:60])
