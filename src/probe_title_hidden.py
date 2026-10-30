# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("人物总数", c.execute("select count(*) from pages where type='人物'").fetchone()[0],
      "| 隐藏", c.execute("select count(*) from pages where type='人物' and hidden=1").fetchone()[0],
      "| 可见", c.execute("select count(*) from pages where type='人物' and hidden=0").fetchone()[0])
print("有称号", c.execute("select count(*) from pages where title<>''").fetchone()[0])
print("\n带称号的条目：")
for nm, ti in c.execute("select name,title from pages where title<>'' order by title"):
    print("   %-16s %s" % (nm, ti))
print("\n隐藏里提及最多的 12 个：")
for nm, m in c.execute("""select name,mentions from pages where type='人物' and hidden=1
                          order by mentions desc limit 12"""):
    print("   %-14s %d" % (nm, m))
