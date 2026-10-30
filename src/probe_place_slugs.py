# -*- coding: utf-8 -*-
"""查地点页 slug 命名（是否带「唐门-」前缀）。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
rows = list(c.execute("select slug,name from pages where type='地点' order by slug"))
print("地点页", len(rows))
for r in rows[:15]:
    print("   ", r[0], "|", r[1])
print("\n含 炼丹/正心堂/练功场/讲经堂:")
for r in rows:
    if any(w in r[0] for w in ("炼丹", "正心堂", "练功场", "讲经堂", "后山")):
        print("   ", r[0], "|", r[1])
