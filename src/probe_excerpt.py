# -*- coding: utf-8 -*-
import io, sys, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for slug in ("势力/夺魄门", "势力/马军司", "势力/人间道"):
    r = c.execute("select lead,sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        print("缺", slug); continue
    secs = json.loads(r[1])
    print("\n==", slug, "|", (r[0] or "")[:40])
    print("   sections:", [s.get("h") for s in secs][:8])
    for s in secs:
        if s.get("h") == "原文摘录":
            for row in (s.get("rows") or [])[:3]:
                print("     -", row.get("note", "")[:70], "|", row.get("title", ""))
print("\n有原文摘录的势力页:", c.execute("select count(*) from pages where slug like '势力/%' and sections like '%原文摘录%'").fetchone()[0])
