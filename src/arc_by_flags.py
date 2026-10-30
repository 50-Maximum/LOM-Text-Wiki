# -*- coding: utf-8 -*-
"""旗标推阶段：支线场景的 requires 旗标，在哪个阶段被置位，就归哪一段。"""
import io, json, os, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
sf = json.load(open(os.path.join(B, "scene_flags.json"), encoding="utf-8"))
facet = {r["sort_key"]: r["facet"] for r in c.execute("select sort_key,facet from pages where type='场景'")}
chap = {r["script"]: (r["chapter"] or "") for r in c.execute("select script,chapter from scenes")}

# 旗标 → 置位场景
setter = collections.defaultdict(list)
for sc, v in sf.items():
    for fl in (v.get("sets") or {}):
        setter[fl].append(sc)

proposals = collections.defaultdict(list)
noev = 0
for sc, v in sf.items():
    if facet.get(sc) not in ("不限时间", "", None):
        continue
    reqs = [r.get("flag") for r in (v.get("requires") or []) if r.get("flag")]
    if not reqs:
        continue
    stages = set()
    ev = []
    for fl in reqs:
        for st in setter.get(fl, []):
            a = facet.get(st)
            if a and a != "不限时间":
                stages.add(a)
                ev.append((fl, st, a))
    if len(stages) == 1:
        a = stages.pop()
        proposals[a].append((sc, chap.get(sc, ""), ev[:2]))
    else:
        noev += 1

tot = sum(len(v) for v in proposals.values())
print("可按旗标归段的支线场景：%d 条（另有 %d 条旗标指向多个阶段或无落点）" % (tot, noev))
for a, lst in proposals.items():
    print("\n== %s（%d）" % (a, len(lst)))
    for sc, ch, ev in lst[:12]:
        e = "；".join("%s 由 %s 置位" % (f, s) for f, s, _ in ev)
        print("   %-26s 章=%-4s %s" % (sc, ch or "-", e[:80]))
json.dump({a: [[sc, ch, ev] for sc, ch, ev in lst] for a, lst in proposals.items()},
          open(os.path.join(B, "research", "arc_by_flags.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n明细：data\\research\\arc_by_flags.json")
