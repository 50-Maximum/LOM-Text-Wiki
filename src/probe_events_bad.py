# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for kw in ["段考约战", "万里鹏程挑战", "三人道中遇敌", "外姓弟子月度评鉴", "赵活提议攻打"]:
    r = c.execute("select slug,name,facet,infobox,sections from pages where type='事件' and name like ?", ("%" + kw + "%",)).fetchone()
    if not r:
        print("==", kw, "无页")
        continue
    print("==", r["name"], "| facet:", r["facet"])
    print("   infobox:", (r["infobox"] or "")[:300])
    try:
        secs = json.loads(r["sections"] or "[]")
    except Exception:
        secs = []
    for s in secs[:6]:
        print("   【%s】" % (s.get("h") or ""))
        for rw in (s.get("rows") or [])[:3]:
            print("      -", (rw.get("note") or "")[:90], "|", rw.get("script"))
