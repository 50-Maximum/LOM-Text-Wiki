# -*- coding: utf-8 -*-
"""按编号规律补地点：同一编号族里已定地点的场景占绝对多数时，把该族空地点场景补上。
产出 data/place_infer2.json，依据标「编号规律（推断）」，不改动已有判定。"""
import io, ast, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = r"D:\LegendOfMortal Wiki"
SRC = open(os.path.join(BASE, "src", "build_wiki2.py"), encoding="utf-8").read()
PREFIX = ast.literal_eval(re.search(r"PLACE_PREFIX_KEYS = (\(.*?\))\n", SRC, re.S).group(1))

INFER = json.load(open(os.path.join(BASE, "data", "scene_place_infer.json"), encoding="utf-8"))
LOGIC = json.load(open(os.path.join(BASE, "data", "place_logic.json"), encoding="utf-8"))
OV = json.load(open(os.path.join(BASE, "data", "place_override.json"), encoding="utf-8"))
PCANON2 = json.load(open(os.path.join(BASE, "data", "place_edits.json"), encoding="utf-8")).get("rename", {})

con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
scenes = {r["script"]: dict(r) for r in con.execute(
    "select script, title, chapter, place, line_count from scenes")}


def eff_place(sc):
    """现有判定（人工核定 > 推断表 > 逻辑表 > 场景 place 规范名）。"""
    o = OV.get(sc)
    if o is not None:
        return (",".join(o.get("places") or []) or o.get("place") or ""), "人工核定"
    inf = INFER.get(sc) or {}
    if inf.get("place"):
        return inf["place"], "场景标题"
    lg = LOGIC.get(sc) or {}
    if lg.get("place"):
        return lg["place"], lg.get("src") or "逻辑"
    p = (scenes[sc].get("place") or "").strip()
    if p:
        p = PCANON2.get(p, p)
    return p, ("场景地点" if p else "")


def families(sc):
    """由长到短的编号族：ch2_5_2_3 → ch2_5_2 / ch2_5 / ch2。"""
    out = []
    parts = sc.split("_")
    for n in range(len(parts) - 1, 0, -1):
        out.append("_".join(parts[:n]))
    return out


placed = {}
for sc in scenes:
    p, how = eff_place(sc)
    if p:
        placed[sc] = p

# 按族统计
fam = collections.defaultdict(collections.Counter)
fam_n = collections.defaultdict(list)
for sc, p in placed.items():
    for f in families(sc):
        fam[f][p] += 1
        fam_n[f].append(sc)

infer = {}
stats = collections.Counter()
for sc in scenes:
    if sc in placed:
        continue
    if any(sc.lower().startswith(k) for k in PREFIX):
        continue        # 编号能直接定地点的，交给原有逻辑
    best = None
    for f in families(sc):
        c = fam.get(f)
        if not c:
            continue
        tot = sum(c.values())
        top, n = c.most_common(1)[0]
        if tot >= 4 and n / tot >= 0.7:
            best = (f, top, n, tot)
            break
    if best:
        f, top, n, tot = best
        infer[sc] = {"place": top, "src": "编号规律（推断）",
                     "family": f, "support": "%d/%d" % (n, tot)}
        stats[f.split("_")[0]] += 1

out = os.path.join(BASE, "data", "place_infer2.json")
json.dump(infer, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("已定地点场景:", len(placed), "/", len(scenes))
print("新增推断:", len(infer), "场 →", out)
print("按一级族分布:", dict(stats.most_common(12)))
for k in list(infer)[:12]:
    print("   %-22s → %-10s (%s)" % (k, infer[k]["place"], infer[k]["support"]))
