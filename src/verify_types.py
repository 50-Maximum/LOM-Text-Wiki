# -*- coding: utf-8 -*-
"""第 7 批最终核验：区域档、类型档、总数一致性。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
q = ("select count(*) from pages where type='地点' and hidden=0 "
     "and slug not in (select slug from place_children)")
top = c.execute(q).fetchone()[0]
reg = c.execute("select facet,count(*) from pages where type='地点' and hidden=0 "
                "and slug not in (select slug from place_children) group by facet order by 2 desc").fetchall()
typ = c.execute("select facet2,count(*) from pages where type='地点' and hidden=0 "
                "and slug not in (select slug from place_children) group by facet2 order by 2 desc").fetchall()
print("顶层地点:", top, "| 区域求和:", sum(x[1] for x in reg), "| 类型求和:", sum(x[1] for x in typ))
print("区域:", ", ".join("%s %d" % x for x in reg))
print("类型:", ", ".join("%s %d" % x for x in typ))
