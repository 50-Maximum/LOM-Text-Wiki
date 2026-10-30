# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
for p in (r"D:\LegendOfMortal Wiki\data\wiki.db",
          r"D:\LegendOfMortal Wiki\dist\活侠传Wiki\data\wiki.db"):
    c = sqlite3.connect("file:" + p.replace("\\", "/") + "?mode=ro", uri=True).cursor()
    print(p)
    print("  群众条目 hidden 分布:",
          c.execute("select hidden,count(*) from pages where type='人物' group by 1").fetchall())
    rows = c.execute("""select name,hidden from pages where type='人物'
                        and (name like '%路人%' or name like '%弟子%') limit 8""").fetchall()
    print("  ", rows)
    q = c.execute("""select count(*) from pages where hidden=0 and (name like ? or lead like ?
                     or slug in (select slug from aliases where alias like ?))""",
                  ("%路人%", "%路人%", "%路人%")).fetchone()
    print("  过滤后命中:", q)
