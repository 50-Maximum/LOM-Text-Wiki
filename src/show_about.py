# -*- coding: utf-8 -*-
"""读「关于本站」页全文，供搬到首页。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
r = c.execute("select slug,name,lead,infobox,sections from pages where slug like ? or name=?",
              ("%关于%", "关于本站")).fetchone()
if not r:
    print("没有关于页")
    raise SystemExit
print("slug:", r["slug"], "| name:", r["name"])
print("LEAD:", r["lead"])
print("INFO:", r["infobox"])
for s in json.loads(r["sections"] or "[]"):
    print("\n== %s ==" % s.get("h"))
    if s.get("html"):
        print(s["html"][:800])
    for x in (s.get("rows") or [])[:8]:
        print("   -", str(x)[:160])
