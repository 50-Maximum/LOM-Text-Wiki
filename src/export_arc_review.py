# -*- coding: utf-8 -*-
"""导出投票定阶段的事件清单（含依据），供人工复核。"""
import io, json, os, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
arcs = json.load(open(os.path.join(B, "arcs.json"), encoding="utf-8"))
order = arcs["arcs"]
ARC_SC = arcs.get("scene") or {}
ch = {r["script"]: (r["chapter"] or "") for r in c.execute("select script,chapter from scenes")}
place = {r["script"]: (r["place"] or "") for r in c.execute("select script,place from scenes")}
title = {r["script"]: (r["title"] or "") for r in c.execute("select script,title from scenes")}
bad = json.load(open(os.path.join(B, "research", "arc_by_vote.json"), encoding="utf-8"))

out = ["# 阶段投票复核清单\n"]
for arc in order:
    lst = bad.get(arc) or []
    if not lst:
        continue
    out.append("\n## %s（%d 条）\n" % (arc, len(lst)))
    for nm, sc, ti, pl in lst:
        out.append("- %s｜场景：%s｜地点：%s｜%s" % (nm, ti or sc, pl or "（未定）", sc))
open(os.path.join(B, "research", "arc_review.md"), "w", encoding="utf-8").write("\n".join(out))
print("已写 data\\research\\arc_review.md，共 %d 条" % sum(len(v) for v in bad.values()))
