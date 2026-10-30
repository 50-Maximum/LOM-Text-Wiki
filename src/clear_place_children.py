# -*- coding: utf-8 -*-
"""清空 place_children：列表接口用它排除子级页，导致地点列表只剩 108 个、
按上级筛选时更是什么都筛不出来。层级已由 facet/上级字段表达，这张表不再需要。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(p)
n = c.execute("select count(*) from place_children").fetchone()[0]
c.execute("delete from place_children")
c.commit()
print("place_children 原有 %d 行，已清空" % n)
print("地点页", c.execute("select count(*) from pages where type='地点' and hidden=0").fetchone()[0],
      "势力页", c.execute("select count(*) from pages where type='势力' and hidden=0").fetchone()[0])
