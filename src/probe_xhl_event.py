# -*- coding: utf-8 -*-
"""收徒事件跨阶段：把它的场景统一到同一阶段。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
r = c.execute("select sections from pages where type='事件' and name like '%夏侯兰收赵活为徒%'").fetchone()
scs = []
if r:
    for s in json.loads(r["sections"] or "[]"):
        for rw in (s.get("rows") or []):
            if rw.get("script") and rw["script"] not in scs:
                scs.append(rw["script"])
print("场景：", scs)
for sc in scs:
    x = c.execute("select chapter,title,script from scenes where script=?", (sc,)).fetchone()
    p = c.execute("select facet from pages where type='场景' and sort_key=?", (sc,)).fetchone()
    print("   %-24s 章=%-6s 阶段=%-8s 题=%s" % (sc, x["chapter"] if x else "-",
                                          p["facet"] if p else "-", (x["title"] if x else "")[:16]))
