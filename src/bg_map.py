# -*- coding: utf-8 -*-
"""统计「背景资源 → 地点」的对应关系，看背景能不能用来反推地点。"""
import io, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
BG = json.load(open(os.path.join(BASE, "data", "scene_bg.json"), encoding="utf-8"))

INFER = json.load(open(os.path.join(BASE, "data", "scene_place_infer.json"), encoding="utf-8"))
LOGIC = json.load(open(os.path.join(BASE, "data", "place_logic.json"), encoding="utf-8"))
OV = json.load(open(os.path.join(BASE, "data", "place_override.json"), encoding="utf-8"))
I2 = json.load(open(os.path.join(BASE, "data", "place_infer2.json"), encoding="utf-8"))
I3 = json.load(open(os.path.join(BASE, "data", "place_infer3.json"), encoding="utf-8"))
I4 = json.load(open(os.path.join(BASE, "data", "place_infer4.json"), encoding="utf-8"))
ED = json.load(open(os.path.join(BASE, "data", "place_edits.json"), encoding="utf-8"))
RENAME = ED.get("rename", {})

con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
scenes = {r["script"]: dict(r) for r in con.execute("select script,chapter,place from scenes")}


def explicit(sc):
    o = OV.get(sc)
    if o is not None:
        return ",".join(o.get("places") or []) or o.get("place") or ""
    for src in (INFER.get(sc), LOGIC.get(sc), I4.get(sc), I3.get(sc), I2.get(sc)):
        if src and src.get("place"):
            return src["place"]
    p = (scenes[sc].get("place") or "").strip()
    return RENAME.get(p, p)


bg_place = collections.defaultdict(collections.Counter)
for sc, bgs in BG.items():
    p = explicit(sc)
    if not p or sc not in scenes:
        continue
    for b in set(bgs):
        bg_place[b][p] += 1

print("背景数:", len(bg_place))
rows = []
for b, c in bg_place.items():
    tot = sum(c.values())
    top, n = c.most_common(1)[0]
    rows.append((b, tot, n / tot, top, c))
rows.sort(key=lambda x: -x[1])
print("\n%-20s %4s %5s  %s" % ("背景", "场次", "纯度", "多数地点"))
for b, tot, share, top, c in rows[:35]:
    print("%-20s %4d %5.0f%%  %-12s %s" % (b, tot, share * 100, top,
                                           "" if share >= 0.8 else str(c.most_common(3))))
