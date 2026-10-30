# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for nm in ("孟瞋", "温无畏", "阮蛋", "阿叔", "唐鹿", "米欧宽", "明玉夫人", "觉慧方丈", "觉醒禅师"):
    r = c.execute("select slug,name,mentions,substr(lead,1,40) from pages where name like ?",
                  ("%" + nm,)).fetchone()
    print("  %-6s %s" % (nm, r))
print("\n别名核对:")
for a in ("明玉", "觉慧", "觉醒"):
    print("  ", a, c.execute("select slug from aliases where alias=?", (a,)).fetchone())
print("\n人物总数", c.execute("select count(*) from pages where type='人物'").fetchone()[0])
