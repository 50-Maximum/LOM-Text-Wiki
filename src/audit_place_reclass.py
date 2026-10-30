# -*- coding: utf-8 -*-
"""弱证据地点：按「现标地点在正文里一次都没出现，而另一地点反复出现」打分，
产出可核对的候选改判清单（不直接改库）。"""
import io, ast, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = r"D:\LegendOfMortal Wiki"
SRC = open(os.path.join(BASE, "src", "build_wiki2.py"), encoding="utf-8").read()
PREFIX = ast.literal_eval(re.search(r"PLACE_PREFIX_KEYS = (\(.*?\))\n", SRC, re.S).group(1))
INFER = json.load(open(os.path.join(BASE, "data", "scene_place_infer.json"), encoding="utf-8"))
LOGIC = json.load(open(os.path.join(BASE, "data", "place_logic.json"), encoding="utf-8"))

con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
scenes = {r["script"]: dict(r) for r in con.execute(
    "select script, chapter, place, title, cjk from scenes")}

# 地点名表：地点页 + 常见简称
places = [r["name"] for r in con.execute("select name from pages where type='地点'")]
ALIAS = {"唐门": ["唐门", "唐家", "本门", "门中"], "崆峒山": ["崆峒"],
         "青城山": ["青城"], "峨嵋山": ["峨嵋", "峨眉"], "点苍山": ["点苍"],
         "江陵": ["江陵"], "襄阳": ["襄阳"], "大理": ["大理"], "天府": []}
NP = collections.OrderedDict()
for p in sorted(set(places), key=len, reverse=True):
    NP[p] = [p] + ALIAS.get(p, [])
seen = set()
CANON = []
for p, al in NP.items():
    base = p.split("-")[-1]
    if base in seen:
        continue
    seen.add(base)
    CANON.append((p, al))
print("候选地点名 %d" % len(CANON))

weak = []
for sc, d in scenes.items():
    pl = (d.get("place") or "").strip()
    if not pl:
        continue
    low = sc.lower()
    if any(low.startswith(k) for k in PREFIX):
        continue
    if (INFER.get(sc) or {}).get("place") or (LOGIC.get(sc) or {}).get("place"):
        continue
    weak.append(sc)

rows = []
for sc in weak:
    d = scenes[sc]
    cur = d["place"].split("-")[-1]
    lines = [(r["seq"], r["text"] or "") for r in con.execute(
        "select seq, text from lines where script=? order by seq", (sc,))]
    full = "\n".join(t for _, t in lines)
    cnt = collections.Counter()
    for name, al in CANON:
        base = name.split("-")[-1]
        for a in al:
            c = full.count(a)
            if c:
                cnt[base] += c
    self_hit = cnt.get(cur, 0)
    others = [(k, v) for k, v in cnt.items() if k != cur and v >= 2]
    others.sort(key=lambda x: -x[1])
    if self_hit == 0 and others:
        rows.append({"script": sc, "title": d["title"] or "", "chapter": d["chapter"] or "",
                     "cur": d["place"], "self": 0, "other": others[:3],
                     "cjk": d["cjk"] or 0,
                     "quote": next((t[:100] for _, t in lines if any(a in t for a in dict((n, a) for n, a in CANON).get(others[0][0], [others[0][0]]))), "")})

rows.sort(key=lambda r: (-r["other"][0][1], -r["cjk"]))
print("现标地点在正文零出现、他地≥2 次的场景 %d 个\n" % len(rows))
out = os.path.join(BASE, "data", "place_reclass_candidates.md")
with open(out, "w", encoding="utf-8") as f:
    f.write("弱证据地点改判候选（现标地名在正文中 0 次出现，另一个地名≥2 次）\n\n")
    for i, r in enumerate(rows, 1):
        f.write("%d. %s｜%s｜%d 字\n" % (i, r["title"] or r["script"], r["chapter"], r["cjk"]))
        f.write("   脚本 %s\n   现标：%s　疑似：%s\n" % (r["script"], r["cur"],
                                              "、".join("%s×%d" % (k, v) for k, v in r["other"])))
        f.write("   例句：%s\n\n" % r["quote"])
print("清单:", out)
for r in rows[:20]:
    print("%-24s %-8s→%-8s %s  | %s"
          % ((r["title"] or r["script"])[:22], r["cur"][:7],
             ",".join("%s×%d" % (k, v) for k, v in r["other"][:2]),
             r["chapter"][:4], r["quote"][:40]))
