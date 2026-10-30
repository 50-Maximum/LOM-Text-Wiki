# -*- coding: utf-8 -*-
"""随机抽样看页面质量。"""
import io, sys, sqlite3, json, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
random.seed(7)
rows = c.execute("select slug,name,lead,infobox,sections from pages order by random() limit 4").fetchall()
for slug, nm, lead, inf, secs in rows:
    print("\n=====", slug, "|", nm)
    print(" 导语:", (lead or "")[:120])
    print(" 信息框:", (inf or "")[:150])
    S = json.loads(secs or "[]")
    for s in S[:4]:
        print("  [%s] %s" % (s.get("h"), ((s.get("html") or "")[:80] or "")))
        for r in (s.get("rows") or [])[:3]:
            print("      -", (r.get("note") or "")[:80], "|", (r.get("title") or "")[:20])
