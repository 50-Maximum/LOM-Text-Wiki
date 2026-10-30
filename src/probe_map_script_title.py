# -*- coding: utf-8 -*-
"""无名地图事件 → 对应剧本 → 场景标题，看能否用剧本标题补名。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
items = json.load(open(os.path.join(BASE, "data", "position_events.json"), encoding="utf-8"))
pm = json.load(open(os.path.join(BASE, "data", "position_script_map.json"), encoding="utf-8"))
try:
    fam = json.load(open(os.path.join(BASE, "data", "position_script_family.json"), encoding="utf-8"))
except Exception:
    fam = {}
print("事件 %d  map %d  family %d" % (len(items), len(pm), len(fam)))
for k in list(pm)[:3]:
    print("   map:", k, "→", pm[k])
for k in list(fam)[:3]:
    print("   fam:", k, "→", str(fam[k])[:120])

c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row
no = [x for x in items if not (x.get("dev") or "").strip()]
hit = 0
print("\n无原生名抽样:")
for x in no[:15]:
    nm = x["name"]
    sc = pm.get(nm)
    t = ""
    if sc:
        r = c.execute("select title,line_count from scenes where script=?", (sc,)).fetchone()
        if r:
            t = "%s（%d句）" % (r["title"], r["line_count"])
            hit += 1
    print("   %-24s key=%-10s → %-30s %s" % (nm, x.get("key"), sc or "-", t))

# 全量可覆盖数
cov = 0
for x in no:
    sc = pm.get(x["name"])
    if sc and c.execute("select 1 from scenes where script=?", (sc,)).fetchone():
        cov += 1
print("\n无原生名 %d 条中，能对上剧本且剧本有场景页的: %d" % (len(no), cov))
