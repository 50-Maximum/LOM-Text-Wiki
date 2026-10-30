# -*- coding: utf-8 -*-
import io, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
for kw in ["上官萤", "负债", "东瀛"]:
    print("== guide_events 含「%s」 ==" % kw)
    for r in c.execute("select id,name,year,month,xun,cond,body from guide_events where body like ? or name like ? or cond like ? limit 6",
                       ("%" + kw + "%", "%" + kw + "%", "%" + kw + "%")):
        print("   [%s] %s｜%s年%s月%s" % (r["id"], r["name"], r["year"], r["month"], r["xun"]))
        print("       cond:", (r["cond"] or "")[:100])
        print("       body:", (r["body"] or "").replace("\n", " ")[:200])
