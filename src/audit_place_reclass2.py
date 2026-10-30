# -*- coding: utf-8 -*-
"""弱证据地点改判候选（修正版）：
把「崆峒山/崆峒」这类同一地点的不同写法归并后再统计，
避免把「崆峒山」当成不是崆峒而误报。"""
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
places = [r["name"] for r in con.execute("select name from pages where type='地点'")]

SUFFIX = ("山", "宫", "寺", "镇", "池", "楼", "阁", "院", "城", "门", "庄", "寨", "洞", "峡", "谷", "峰")
EXTRA = {"唐门": ["唐家", "本门"], "崆峒山": ["崆峒"], "青城山": ["青城"],
         "峨嵋山": ["峨嵋", "峨眉"], "点苍山": ["点苍"]}


def variants(name):
    base = name.split("-")[-1]
    out = {base, name}
    for suf in SUFFIX:
        if base.endswith(suf) and len(base) - len(suf) >= 2:
            out.add(base[: -len(suf)])
    for a in EXTRA.get(base, []):
        out.add(a)
    return sorted({x for x in out if len(x) >= 2}, key=len, reverse=True)


def count_places(text, canon):
    """长名优先，命中后抹掉，避免重复计数。"""
    t = text
    cnt = collections.Counter()
    order = sorted(canon, key=lambda x: -len(x[0]))
    for name, vs in order:
        for v in vs:
            n = t.count(v)
            if n:
                cnt[name] += n
                t = t.replace(v, "\u0000")
    return cnt


CANON = [(p.split("-")[-1], variants(p)) for p in places]
CANON = list({c[0]: c for c in CANON}.values())
VAR2NAME = {}
for _nm, _vs in CANON:
    for _v in _vs:
        VAR2NAME.setdefault(_v, _nm)

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
    cur_name = VAR2NAME.get(cur, cur)
    lines = [(r["seq"], r["text"] or "") for r in con.execute(
        "select seq, text from lines where script=? order by seq", (sc,))]
    full = "\n".join(t for _, t in lines)
    cnt = count_places(full, CANON)
    self_hit = cnt.get(cur_name, 0)
    others = sorted(((k, v) for k, v in cnt.items() if k != cur_name and v >= 2),
                    key=lambda x: -x[1])
    if self_hit == 0 and others:
        rows.append({"script": sc, "title": d["title"] or "", "chapter": d["chapter"] or "",
                     "cur": d["place"], "other": others[:3], "cjk": d["cjk"] or 0,
                     "quote": next((t[:110] for _, t in lines
                                    if any(v in t for v in dict(CANON)[others[0][0]])), "")})

rows.sort(key=lambda r: (-r["other"][0][1], -r["cjk"]))
out = os.path.join(BASE, "data", "place_reclass_candidates.md")
with open(out, "w", encoding="utf-8") as f:
    f.write("弱证据地点改判候选：现标地名在正文出现 0 次，另一地名反复出现\n\n")
    f.write("共 %d 场（按他地出现次数降序）\n\n" % len(rows))
    for i, r in enumerate(rows, 1):
        f.write("%d. %s｜%s｜%d 字\n" % (i, r["title"] or r["script"], r["chapter"], r["cjk"]))
        f.write("   脚本 %s\n   现标：%s　另有：%s\n" % (r["script"], r["cur"],
                                               "、".join("%s×%d" % (k, v) for k, v in r["other"])))
        f.write("   例句：%s\n\n" % r["quote"])
print("候选 %d 场 -> %s" % (len(rows), out))
for r in rows[:18]:
    print("%-22s %-8s -> %-16s %s"
          % ((r["title"] or r["script"])[:20], r["cur"][:6],
             ",".join("%s×%d" % (k, v) for k, v in r["other"][:2]), r["chapter"][:4]))
