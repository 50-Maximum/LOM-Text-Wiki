# -*- coding: utf-8 -*-
"""列出「靠投票定阶段」的事件（场景全是支线/其他），按阶段分组，便于逐段抽查。"""
import io, json, os, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
arcs = json.load(open(os.path.join(B, "arcs.json"), encoding="utf-8"))
ARC_SC = arcs.get("scene") or {}
ch = {r["script"]: (r["chapter"] or "") for r in c.execute("select script,chapter from scenes")}
place = {r["script"]: (r["place"] or "") for r in c.execute("select script,place from scenes")}
title = {r["script"]: (r["title"] or "") for r in c.execute("select script,title from scenes")}

rows = []
for r in c.execute("select name,facet,sections from pages where type='事件'"):
    try:
        secs = json.loads(r["sections"] or "[]")
    except Exception:
        continue
    scs = []
    for s in secs:
        for rw in (s.get("rows") or []):
            sc = rw.get("script")
            if sc and sc in ch and sc not in scs:
                scs.append(sc)
    if not scs:
        continue
    if r["facet"] in ("", "不限时间"):
        continue
    if all((ch.get(x) in ("支线", "其他", "角色线")) and x not in ARC_SC for x in scs):
        rows.append((r["facet"], r["name"], scs[0], title.get(scs[0], "")[:18], place.get(scs[0], "")))

by = collections.defaultdict(list)
for facet, nm, sc, ti, pl in rows:
    by[facet].append((nm, sc, ti, pl))
print("投票定阶段的事件：%d 条" % len(rows))
for arc in arcs["arcs"]:
    if arc not in by:
        continue
    print("\n== %s（%d）==" % (arc, len(by[arc])))
    for nm, sc, ti, pl in by[arc][:25]:
        print("   %-24s %-22s %s" % (nm[:24], ti, pl))
json.dump({k: v for k, v in by.items()},
          open(os.path.join(B, "research", "arc_by_vote.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
