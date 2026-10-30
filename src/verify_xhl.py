# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
r = c.execute("select name,sections from pages where type='人物' and name like '%夏侯兰%'").fetchone()
secs = json.loads(r["sections"] or "[]")
print("夏侯兰页 章数：", len(secs))
for s in secs:
    h = s.get("h") or ""
    if h[:2] in ("0 ", "1 ", "10", "11", "12"):
        rows = s.get("rows") or []
        print("  【%s】%d 行" % (h, len(rows)))
        for rw in rows[:3]:
            print("      -", (rw.get("note") or rw.get("title") or "")[:60])
print("\n占位页是否清掉：")
for nm in ["铁拳门·掌门", "玄功门·掌门"]:
    print("   ", nm, "仍在" if c.execute("select 1 from pages where name=?", (nm,)).fetchone() else "已清")
