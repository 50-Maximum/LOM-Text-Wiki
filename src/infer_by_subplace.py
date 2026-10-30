# -*- coding: utf-8 -*-
"""① placeset 补入新建地点；② 正文地名词自动判定（data/place_infer6.json）。"""
import io, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
D = os.path.join(BASE, "data")

# ---------- ① patch placeset ----------
S = os.path.join(BASE, "src", "build_wiki2.py")
s = open(S, encoding="utf-8").read()
old = 'placeset = {n for (t, n) in byname if t == "地点"}'
if "PE_NEW if x.get" not in s:
    assert old in s
    s = s.replace(old, old[:-1] + ' | {x.get("name") for x in PE_NEW if x.get("name")}', 1)
    print("placeset 已补新建地点")

# 载入 place_infer6（正文地名词）
if "PLACE_INFER6" not in s:
    a = "PLACE_INFER5 = {}"
    i = s.find(a)
    j = s.find("\n", s.find("except Exception:", i))
    j = s.find("\n", j + 1) + 1
    ins = '''
PLACE_INFER6 = {}
try:
    _pi6 = os.path.join(BASE, "data", "place_infer6.json")
    if os.path.exists(_pi6):
        PLACE_INFER6 = json.load(open(_pi6, encoding="utf-8"))
except Exception:
    PLACE_INFER6 = {}
'''
    s = s[:j] + ins + s[j:]
    print("已载入 PLACE_INFER6")

if "PLACE_INFER6.get(script)" not in s:
    tail = '    _i5 = PLACE_INFER5.get(script) or {}'
    assert tail in s
    s = s.replace(tail, '''    _i6 = PLACE_INFER6.get(script) or {}
    if _i6.get("place"):
        return pcanon(_i6["place"]), "正文地名（推断）"
''' + tail, 1)
    print("place_of 已接正文地名")

open(S, "w", encoding="utf-8").write(s)

# ---------- ② 生成 place_infer6 ----------
con = sqlite3.connect(os.path.join(D, "wiki.db"))
con.row_factory = sqlite3.Row
places = sorted(r[0] for r in con.execute("select name from pages where type='地点'"))
PE = json.load(open(os.path.join(D, "place_edits.json"), encoding="utf-8"))
RENAME = PE.get("rename") or {}

ALIAS = {}
for p in places:
    if "-" in p:
        ALIAS.setdefault(p.split("-", 1)[1], p)
for k, v in RENAME.items():
    ALIAS[k] = v
# 明确歧义词不用
for bad in ["正心堂", "无色广场", "飞天殿"]:
    ALIAS.pop(bad, None)
ALIAS.setdefault("无色广场", "崆峒-无色广场")
ALIAS.setdefault("正心堂", "唐门-正心堂")

scenes = {r[0]: r for r in con.execute("select script,title from scenes")}
# 已有地点（人工/覆盖/推断各层）
have = set()
for f in ["place_manual.json", "place_override.json", "scene_place_infer.json",
          "place_logic.json", "place_infer2.json", "place_infer3.json",
          "place_infer4.json", "place_infer5.json"]:
    p = os.path.join(D, f)
    if os.path.exists(p):
        have |= set(json.load(open(p, encoding="utf-8")).keys())

texts = collections.defaultdict(list)
for r in con.execute("select script,text from lines order by script,seq"):
    if r["script"] in scenes:
        texts[r["script"]].append(r["text"] or "")

out = {}
for sc, ls in texts.items():
    if sc in have:
        continue
    body = " ".join(ls)
    hits = {}
    for al, p in ALIAS.items():
        n = body.count(al)
        if n:
            hits[p] = hits.get(p, 0) + n
    if not hits:
        continue
    rank = sorted(hits.items(), key=lambda x: -x[1])
    top, n1 = rank[0]
    if len(rank) > 1 and rank[1][1] == n1:
        continue
    out[sc] = {"place": top, "src": "正文地名（推断）",
               "why": "正文出现「%s」%d 次" % (top.split("-")[-1], n1), "hit": n1}

json.dump(out, open(os.path.join(D, "place_infer6.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, sort_keys=True)
print("未定场次可判", len(out), "条")
print(collections.Counter(v["place"] for v in out.values()).most_common(12))
for k in list(out)[:10]:
    print("   %-24s → %-14s %s" % (k, out[k]["place"], out[k]["why"]))
