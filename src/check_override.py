# -*- coding: utf-8 -*-
"""核对人工核定的四场：页面里是否出现「人工核定」并指向新地点。"""
import io, sqlite3, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row
print("含「人工核定」的页面数:",
      con.execute("select count(*) from pages where sections like '%人工核定%' "
                  "or infobox like '%人工核定%'").fetchone()[0])
for r in con.execute("select slug from pages where sections like '%人工核定%' or infobox like '%人工核定%' limit 12"):
    print("   ", r["slug"])
print()
for sc in ("ch4_4_1", "ch4_1_3", "ch7_2_4", "ch2_4_4_1"):
    rows = con.execute("select slug, sections from pages where sections like ? limit 3", ("%" + sc + "%",)).fetchall()
    for r in rows:
        secs = json.loads(r["sections"])
        for s in secs:
            for row in (s.get("rows") or []):
                if row.get("script") == sc:
                    print("%-40s %s | %s" % (r["slug"], s.get("h"), row.get("note")))
