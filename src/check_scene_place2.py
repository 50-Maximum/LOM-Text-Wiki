# -*- coding: utf-8 -*-
"""打印场景页「场景信息」里的各行，确认地点改判生效。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for slug in ("场景/ch5_4_2", "场景/S0703_01", "场景/S0101_01", "场景/S2321_04_02_01"):
    r = c.execute("select sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        print("缺", slug)
        continue
    print("=" * 60, slug)
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") != "场景信息":
            continue
        for row in (s.get("rows") or []):
            print("   %s" % (row.get("note") or row.get("title") or row))
        if s.get("html"):
            print("   [html]", s["html"][:300])
