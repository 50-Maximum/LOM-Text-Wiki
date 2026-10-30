# -*- coding: utf-8 -*-
import io, sys, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for t in ("人物", "地点", "势力", "事件", "场景", "地图事件", "书物", "物品",
          "武学", "成就", "战斗角色", "数值"):
    rows = c.execute("""select facet,count(*) n from pages
                        where type=? and hidden=0 and facet<>''
                        group by 1 order by 2 desc limit 8""", (t,)).fetchall()
    tot = c.execute("select count(*) from pages where type=? and hidden=0", (t,)).fetchone()[0]
    blank = c.execute("""select count(*) from pages where type=? and hidden=0 and (facet='' or facet is null)""",
                      (t,)).fetchone()[0]
    print("%-6s 共%-4d 无分类%-3d  %s" % (t, tot, blank,
          " | ".join("%s:%d" % (a, b) for a, b in rows)))
