# -*- coding: utf-8 -*-
"""导出地点列表（含 lead），供区域再归类。"""
import io, sqlite3, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
rows = con.execute("select slug,name,lead,facet from pages where type='地点' order by name").fetchall()
kids = {r[0] for r in con.execute("select slug from place_children")}
out = []
for r in rows:
    out.append({"slug": r["slug"], "name": r["name"],
                "top": r["slug"] not in kids,
                "facet": r["facet"], "lead": (r["lead"] or "")[:300]})
json.dump(out, open(r"D:\LegendOfMortal Wiki\data\_places_lead.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
other = [o for o in out if o["top"] and o["facet"] == "其他"]
print("顶层总数", sum(1 for o in out if o["top"]), "| 其他", len(other))
for o in other:
    print("・%s :: %s" % (o["name"], o["lead"].replace("\n", " ")))
