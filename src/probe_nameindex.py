# -*- coding: utf-8 -*-
import io, sys, sqlite3, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
sql = ("select name,slug from pages where type in "
       "('势力','地点','书物','物品','武学','装备') "
       "and length(name) between 2 and 10 "
       "union all "
       "select alias as name, slug from aliases "
       "where length(alias) between 2 and 10 "
       "order by length(name) desc")
try:
    rows = c.execute(sql).fetchall()
    print("ok", len(rows))
except Exception:
    traceback.print_exc()
    print("--- 尝试分开查")
    print(c.execute("select count(*) from aliases").fetchone())
    print(c.execute("select * from aliases limit 5").fetchall())
