# -*- coding: utf-8 -*-
"""沿事件链顺延地点：只要上一场/下一场有地点且本场没有相反证据，就沿用。
规则（按五零的意思）：没写改变地点，就当作没改变。
产出 data/place_infer4.json。"""
import io, ast, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = r"D:\LegendOfMortal Wiki"
SRC = open(os.path.join(BASE, "src", "build_wiki2.py"), encoding="utf-8").read()
PREFIX = ast.literal_eval(re.search(r"PLACE_PREFIX_KEYS = (\(.*?\))\n", SRC, re.S).group(1))

INFER = json.load(open(os.path.join(BASE, "data", "scene_place_infer.json"), encoding="utf-8"))
LOGIC = json.load(open(os.path.join(BASE, "data", "place_logic.json"), encoding="utf-8"))
OV = json.load(open(os.path.join(BASE, "data", "place_override.json"), encoding="utf-8"))
I2 = json.load(open(os.path.join(BASE, "data", "place_infer2.json"), encoding="utf-8"))
I3 = json.load(open(os.path.join(BASE, "data", "place_infer3.json"), encoding="utf-8"))
EDITS = json.load(open(os.path.join(BASE, "data", "place_edits.json"), encoding="utf-8"))
RENAME = EDITS.get("rename", {})
NXT = json.load(open(os.path.join(BASE, "data", "scene_next.json"), encoding="utf-8"))

con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
scenes = {r["script"]: dict(r) for r in con.execute(
    "select script,title,chapter,place from scenes")}
places = [r["name"] for r in con.execute("select name from pages where type='地点'")]

REV = collections.defaultdict(list)
for s, d in NXT.items():
    t = (d or {}).get("next")
    if t:
        REV[t].append(s)

CANON = {"崆峒": "崆峒山", "青城": "青城山", "夺魄": "崆峒-夺魄森林",
         "森林": "崆峒-夺魄森林", "正心堂": "唐门-正心堂", "练功场": "唐门-练功场",
         "大门": "唐门-大门", "后山": "唐门-后山", "外堡": "唐门-外堡",
         "弟子房": "唐门-弟子房", "女弟子房": "唐门-弟子房", "药铺": "唐门-药铺",
         "伙房": "唐门-伙房", "锻冶场": "唐门-锻冶场", "讲经堂": "唐门-讲经堂",
         "茶肆": "唐门-茶肆", "闹市": "唐门-闹市", "温泉": "唐门-温泉"}


def norm(x):
    x = (x or "").strip()
    x = RENAME.get(x, x)
    return CANON.get(x, x)


def explicit(sc):
    o = OV.get(sc)
    if o is not None:
        return norm(",".join(o.get("places") or []) or o.get("place") or "")
    for src in (INFER.get(sc), LOGIC.get(sc), I2.get(sc), I3.get(sc)):
        if src and src.get("place"):
            return norm(src["place"])
    return norm(scenes[sc].get("place") or "")


# 正文地名统计
SUF = ("山", "宫", "寺", "镇", "池", "楼", "阁", "院", "城", "门", "庄", "寨", "洞", "峡", "谷", "峰")
EXTRA = {"唐门": ["唐家"], "崆峒山": ["崆峒"], "青城山": ["青城"], "点苍山": ["点苍"],
         "峨嵋山": ["峨嵋", "峨眉"]}


def variants(name):
    base = name.split("-")[-1]
    out = {name, base}
    for suf in SUF:
        if base.endswith(suf) and len(base) - len(suf) >= 2:
            out.add(base[: -len(suf)])
    out.update(EXTRA.get(base, []))
    return [x for x in out if len(x) >= 2]


CANON_P = {p: variants(p) for p in places}
VAR2NAME = {}
for nm, vs in CANON_P.items():
    for v in vs:
        VAR2NAME.setdefault(v, nm)


def text_places(sc):
    rows = con.execute("select text from lines where script=?", (sc,))
    t = "\n".join((r["text"] or "") for r in rows)
    cnt = collections.Counter()
    for nm, vs in sorted(CANON_P.items(), key=lambda x: -len(x[0])):
        for v in vs:
            n = t.count(v)
            if n:
                cnt[nm] += n
                t = t.replace(v, "\u0000")
    return cnt


place = {}
for sc in scenes:
    p = explicit(sc)
    if p:
        place[sc] = p

print("起始已定:", len(place), "/", len(scenes))
new = {}
for rnd in range(8):
    added = 0
    for sc in scenes:
        if sc in place:
            continue
        if any(sc.lower().startswith(k) for k in PREFIX):
            continue
        # 候选：先看上一场，再看下一场
        cand = None
        for nb in REV.get(sc, []):
            if nb in place:
                cand = place[nb]
                break
        if not cand:
            nx = (NXT.get(sc) or {}).get("next")
            if nx and nx in place:
                cand = place[nx]
        if not cand or cand not in CANON_P:
            continue
        cnt = text_places(sc)
        cur_hit = cnt.get(cand, 0)
        top = cnt.most_common(1)[0] if cnt else (None, 0)
        if top[0] and top[1] >= 2 and top[1] > cur_hit:
            place[sc] = top[0]
            new[sc] = {"place": top[0], "src": "正文线索（顺延改判）",
                       "why": "顺延原为%s，正文另提%s %d 次" % (cand, top[0], top[1])}
        else:
            place[sc] = cand
            new[sc] = {"place": cand, "src": "事件链顺延（推断）",
                       "why": "未出现改变地点的描写，沿用相邻场"}
        added += 1
    print("第 %d 轮 +%d" % (rnd + 1, added))
    if not added:
        break

out = os.path.join(BASE, "data", "place_infer4.json")
json.dump(new, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("新增 %d，总计已定 %d / %d → %s" % (len(new), len(place), len(scenes), out))
print("按依据:", collections.Counter(v["src"] for v in new.values()).most_common())
