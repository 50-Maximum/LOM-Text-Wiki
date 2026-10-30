# -*- coding: utf-8 -*-
"""承前/接续链推断地点：只看紧邻的上一场、下一场，同一章内且候选唯一时才补。
产出 data/place_infer3.json（依据标「承前场（推断）」/「接续场（推断）」）。"""
import io, ast, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = r"D:\LegendOfMortal Wiki"
SRC = open(os.path.join(BASE, "src", "build_wiki2.py"), encoding="utf-8").read()
PREFIX = ast.literal_eval(re.search(r"PLACE_PREFIX_KEYS = (\(.*?\))\n", SRC, re.S).group(1))

INFER = json.load(open(os.path.join(BASE, "data", "scene_place_infer.json"), encoding="utf-8"))
LOGIC = json.load(open(os.path.join(BASE, "data", "place_logic.json"), encoding="utf-8"))
OV = json.load(open(os.path.join(BASE, "data", "place_override.json"), encoding="utf-8"))
INFER2 = json.load(open(os.path.join(BASE, "data", "place_infer2.json"), encoding="utf-8"))
RENAME = json.load(open(os.path.join(BASE, "data", "place_edits.json"), encoding="utf-8")).get("rename", {})
CANON = {"崆峒": "崆峒山", "青城": "青城山", "夺魄": "崆峒-夺魄森林",
         "森林": "崆峒-夺魄森林", "正心堂": "唐门-正心堂", "练功场": "唐门-练功场"}
NXT = json.load(open(os.path.join(BASE, "data", "scene_next.json"), encoding="utf-8"))

con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
scenes = {r["script"]: dict(r) for r in con.execute(
    "select script, title, chapter, place from scenes")}

REV = collections.defaultdict(list)
for s, d in NXT.items():
    t = (d or {}).get("next")
    if t:
        REV[t].append(s)


def base_place(sc):
    o = OV.get(sc)
    if o is not None:
        return (",".join(o.get("places") or []) or o.get("place") or "")
    for src in (INFER.get(sc), LOGIC.get(sc), INFER2.get(sc)):
        if src and src.get("place"):
            return src["place"]
    p = (scenes[sc].get("place") or "").strip()
    p = RENAME.get(p, p)
    return CANON.get(p, p)


place = {}
for sc in scenes:
    p = base_place(sc)
    if p:
        place[sc] = p

print("起始已定地点:", len(place), "/", len(scenes))

new = {}
for _round in range(6):
    added = 0
    for sc in scenes:
        if sc in place:
            continue
        if any(sc.lower().startswith(k) for k in PREFIX):
            continue
        ch = scenes[sc].get("chapter") or ""
        fam = sc.split("_")[0]
        cands = collections.Counter()
        src_kind = {}
        for nb, kind in [(p, "承前场") for p in REV.get(sc, [])] + \
                        [((NXT.get(sc) or {}).get("next"), "接续场")]:
            if not nb or nb not in place:
                continue
            if (scenes.get(nb, {}).get("chapter") or "") != ch:
                continue
            if nb.split("_")[0] != fam and not nb.startswith(fam):
                continue
            cands[place[nb]] += 1
            src_kind.setdefault(place[nb], kind)
        if len(cands) == 1:
            pl = next(iter(cands))
            place[sc] = pl
            new[sc] = {"place": pl, "src": src_kind.get(pl, "承前场") + "（推断）",
                       "why": "紧邻场景同章同族且地点一致"}
            added += 1
    print("第 %d 轮新增 %d" % (_round + 1, added))
    if not added:
        break

out = os.path.join(BASE, "data", "place_infer3.json")
json.dump(new, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("总已定:", len(place), "新增:", len(new), "→", out)
print("按依据:", collections.Counter(v["src"] for v in new.values()).most_common())
for k in list(new)[:10]:
    print("   %-22s → %-10s %s" % (k, new[k]["place"], new[k]["src"]))
