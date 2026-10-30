# -*- coding: utf-8 -*-
"""用「章节 + 背景」联合判断地点：比单看背景纯度高得多，先看纯度和可覆盖面。"""
import io, json, os, sqlite3, sys, collections
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
CANON = {"崆峒": "崆峒山", "青城": "青城山", "夺魄": "崆峒-夺魄森林", "森林": "崆峒-夺魄森林"}

con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
scenes = {r["script"]: dict(r) for r in con.execute("select script,chapter,place from scenes")}
places = {r[0] for r in con.execute("select name from pages where type='地点'")}


def explicit(sc):
    o = OV.get(sc)
    if o is not None:
        return ",".join(o.get("places") or []) or o.get("place") or ""
    for src in (INFER.get(sc), LOGIC.get(sc), I4.get(sc), I3.get(sc), I2.get(sc)):
        if src and src.get("place"):
            return src["place"]
    p = (scenes[sc].get("place") or "").strip()
    p = RENAME.get(p, p)
    return CANON.get(p, p)


known, unknown = {}, []
for sc in scenes:
    p = explicit(sc)
    if p in places:
        known[sc] = p
    else:
        unknown.append(sc)

key = collections.defaultdict(collections.Counter)
for sc, p in known.items():
    ch = scenes[sc].get("chapter") or ""
    for b in set(BG.get(sc, [])):
        key[(ch, b)][p] += 1

usable = {}
for k, c in key.items():
    tot = sum(c.values())
    top, n = c.most_common(1)[0]
    if tot >= 3 and n / tot >= 0.8:
        usable[k] = (top, n, tot)

print("已知地点场景:", len(known), "未知:", len(unknown))
print("可用（章节+背景）键:", len(usable))

hit = collections.Counter()
for sc in unknown:
    ch = scenes[sc].get("chapter") or ""
    votes = collections.Counter()
    for b in set(BG.get(sc, [])):
        u = usable.get((ch, b))
        if u:
            votes[u[0]] += 1
    if votes:
        top, n = votes.most_common(1)[0]
        hit[top] += 1
print("可补场景数:", sum(hit.values()))
print("按地点:", hit.most_common(10))
