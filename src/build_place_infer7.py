# -*- coding: utf-8 -*-
"""补无地点场景：承前场推断（沿剧情边回溯）＋背景资源推断（章节+背景共识）。

规则（依五零铁律）：
- 只走剧情类边 main/scene/story/branch，最多 4 跳；
- 途中任何一场出现转场/动身证据（SetCurrentTravelScript、move+、离开/前往/赶往/动身/出发）即中断；
- 找到的最近祖先必须已有强判据（人工/正文在场/脚本编号/编号规律/驻地级）；
- 背景推断要求同章节同背景 ≥3 场且 ≥80% 指向同一具体场所。
输出 data/place_infer7.json。
"""
import io, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "scripts")
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row
bg = json.load(open(os.path.join(BASE, "data", "scene_bg.json"), encoding="utf-8"))
ch = {r[0]: (r[1] or "") for r in c.execute("select script,chapter from scenes")}

def info(sections):
    for s in json.loads(sections or "[]"):
        if s.get("h") == "场景信息":
            return s.get("html") or ""
    return ""

scene = {}
for r in c.execute("select slug,sections from pages where type='场景'"):
    sc = r["slug"][len("场景/"):]
    t = info(r["sections"])
    m = re.search(r"地点：([^（。]+)（依据：([^）]+)）", t)
    if m:
        scene[sc] = (m.group(1).strip(), m.group(2).strip())

no = [sc for sc in ch if sc not in scene]
print("无地点", len(no))

STRONG = ("人工指定", "人工核定", "正文在场", "脚本编号", "编号规律（推断）",
          "正文地名（推断）", "事件链顺延（推断）", "背景资源（推断）")
TRAVEL = re.compile(r"SetCurrentTravelScript|move\+|离开|前往|赶往|动身|出发|上路|赶路")

inbound = collections.defaultdict(list)
for s, d, t in c.execute("select src,dst,type from scene_edges"):
    if t in ("main", "scene", "story", "branch"):
        inbound[d].append(s)

def travel_hit(sc):
    p = os.path.join(RAW, sc + ".txt")
    if not os.path.exists(p):
        return False
    return bool(TRAVEL.search(open(p, encoding="utf-8", errors="ignore").read()))

out, by_bg = {}, 0
resolved = {}
for sc in no:
    # 1) 背景共识
    b = (bg.get(sc) or [""])[0]
    if b:
        cnt = collections.Counter()
        for o, (p, tier) in scene.items():
            if "-" not in p or tier.startswith(("文中提及", "驻地")):
                continue
            if (bg.get(o) or [""])[0] == b and ch.get(o) == ch.get(sc):
                cnt[p] += 1
        tot = sum(cnt.values())
        if tot >= 3 and cnt:
            top, n = cnt.most_common(1)[0]
            if n / tot >= 0.8:
                out[sc] = {"place": top, "src": "背景资源（推断）", "why": "%s %d/%d" % (b, n, tot)}
                by_bg += 1
                continue
    # 2) 承前场回溯
    seen = {sc}
    frontier = [sc]
    found = None
    for depth in range(4):
        nxt = []
        for cur in frontier:
            for par in inbound.get(cur, []):
                if par in seen:
                    continue
                seen.add(par)
                if travel_hit(cur):
                    continue
                pv = scene.get(par)
                if pv and pv[1] in STRONG:
                    found = (par, pv[0], pv[1])
                    break
                nxt.append(par)
            if found:
                break
        if found:
            break
        frontier = nxt
    if found:
        out[sc] = {"place": found[1], "src": "承前场（推断）", "why": "回溯自 " + found[0]}

json.dump(out, open(os.path.join(BASE, "data", "place_infer7.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)
print("补出 %d 场（背景 %d ／ 承前 %d），仍空 %d" % (len(out), by_bg, len(out) - by_bg, len(no) - len(out)))
for sc, v in list(out.items())[:10]:
    print("   %-30s %-14s %s" % (sc, v["place"], v["src"]))
