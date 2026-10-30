# -*- coding: utf-8 -*-
"""按旗标归段（只采信「置位场景是正章」的证据），其余留待人工核。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
sf = json.load(open(os.path.join(B, "scene_flags.json"), encoding="utf-8"))
facet = {r["sort_key"]: r["facet"] for r in c.execute("select sort_key,facet from pages where type='场景'")}
chap = {r["script"]: (r["chapter"] or "") for r in c.execute("select script,chapter from scenes")}
setter = {}
for sc, v in sf.items():
    for fl in (v.get("sets") or {}):
        setter.setdefault(fl, []).append(sc)

arcs = json.load(open(os.path.join(B, "arcs.json"), encoding="utf-8"))
sc_map = arcs.setdefault("scene", {})

applied, pending = [], []
for sc, v in sf.items():
    if facet.get(sc) not in ("不限时间", "", None):
        continue
    reqs = [r.get("flag") for r in (v.get("requires") or []) if r.get("flag")]
    if not reqs:
        continue
    stages, ev, ok = set(), [], True
    for fl in reqs:
        sts = [s for s in setter.get(fl, [])]
        if not sts:
            ok = False
            break
        for s in sts:
            a = facet.get(s)
            if a and a != "不限时间":
                stages.add(a)
                ev.append((fl, s, a))
            if not (chap.get(s) or "").startswith("第"):
                ok = False
    if len(stages) != 1:
        continue
    a = stages.pop()
    if ok:
        sc_map[sc] = a
        applied.append((sc, a, ev[0]))
    else:
        pending.append((sc, a, ev[0]))

json.dump(arcs, open(os.path.join(B, "arcs.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("按旗标归段（正章置位，可信）：%d 条" % len(applied))
for sc, a, ev in applied[:20]:
    print("   %-26s → %-8s （%s 由 %s 置位）" % (sc, a, ev[0], ev[1]))
print("\n待核（置位场景非正章）：%d 条" % len(pending))
for sc, a, ev in pending[:12]:
    print("   %-26s 参考 %-8s （%s 由 %s 置位）" % (sc, a, ev[0], ev[1]))
json.dump(pending, open(os.path.join(B, "research", "arc_pending.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
