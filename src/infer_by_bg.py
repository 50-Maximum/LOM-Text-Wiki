# -*- coding: utf-8 -*-
"""用「章节 + 背景资源」补地点，产出 data/place_infer5.json。"""
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
CANON = {"崆峒": "崆峒山", "青城": "青城山", "夺魄": "崆峒-夺魄森林",
         "森林": "崆峒-夺魄森林", "大门": "唐门-大门", "外堡": "唐门-外堡",
         "正心堂": "唐门-正心堂", "练功场": "唐门-练功场", "药铺": "唐门-药铺",
         "后山": "唐门-后山", "伙房": "唐门-伙房", "炼丹房": "唐门-炼丹房"}

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

out = {}
for sc in unknown:
    ch = scenes[sc].get("chapter") or ""
    votes = collections.Counter()
    hit_bg = {}
    for b in set(BG.get(sc, [])):
        u = usable.get((ch, b))
        if u:
            votes[u[0]] += 1
            hit_bg[u[0]] = b
    if not votes:
        continue
    top, n = votes.most_common(1)[0]
    if len(votes) > 1 and votes.most_common(2)[0][1] == votes.most_common(2)[1][1]:
        continue
    u = usable[(ch, hit_bg[top])]
    out[sc] = {"place": top, "src": "背景资源（推断）",
               "why": "%s 章内背景 %s 的已知场景 %d/%d 为 %s"
                      % (ch or "无章节", hit_bg[top], u[1], u[2], top)}

p = os.path.join(BASE, "data", "place_infer5.json")
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("未知 %d 场；可由背景补 %d 场 → %s" % (len(unknown), len(out), p))
print("按地点:", collections.Counter(v["place"] for v in out.values()).most_common())
for k in list(out)[:8]:
    print("   %-22s → %-10s %s" % (k, out[k]["place"], out[k]["why"]))
