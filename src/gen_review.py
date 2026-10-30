# -*- coding: utf-8 -*-
"""生成「弱证据地点」人工审查表：每场都带原文，不用再另外去搜。
排除已人工核定的脚本。"""
import io, ast, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = r"D:\LegendOfMortal Wiki"
SRC = open(os.path.join(BASE, "src", "build_wiki2.py"), encoding="utf-8").read()
PREFIX = ast.literal_eval(re.search(r"PLACE_PREFIX_KEYS = (\(.*?\))\n", SRC, re.S).group(1))
INFER = json.load(open(os.path.join(BASE, "data", "scene_place_infer.json"), encoding="utf-8"))
LOGIC = json.load(open(os.path.join(BASE, "data", "place_logic.json"), encoding="utf-8"))
OVP = os.path.join(BASE, "data", "place_override.json")
OV = json.load(open(OVP, encoding="utf-8")) if os.path.exists(OVP) else {}

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
    out.update(EXTRA.get(base, []))
    return sorted({x for x in out if len(x) >= 2}, key=len, reverse=True)


def count_places(text, canon):
    t, cnt = text, collections.Counter()
    for name, vs in sorted(canon, key=lambda x: -len(x[0])):
        for v in vs:
            n = t.count(v)
            if n:
                cnt[name] += n
                t = t.replace(v, "\u0000")
    return cnt


CANON = list({p.split("-")[-1]: (p.split("-")[-1], variants(p)) for p in places}.values())
VAR2NAME = {}
for _nm, _vs in CANON:
    for _v in _vs:
        VAR2NAME.setdefault(_v, _nm)

weak = []
for sc, d in scenes.items():
    pl = (d.get("place") or "").strip()
    if not pl or sc in OV:
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
    cur_name = VAR2NAME.get(d["place"].split("-")[-1], d["place"].split("-")[-1])
    lines = [(r["seq"], r["speaker"] or "", r["text"] or "") for r in con.execute(
        "select seq, speaker, text from lines where script=? order by seq", (sc,))]
    full = "\n".join(t for _, _, t in lines)
    cnt = count_places(full, CANON)
    if cnt.get(cur_name, 0):
        continue
    others = sorted(((k, v) for k, v in cnt.items() if k != cur_name and v >= 2),
                    key=lambda x: -x[1])
    if not others:
        continue
    rows.append({"sc": sc, "d": d, "cur": d["place"], "others": others[:4],
                 "lines": lines})

rows.sort(key=lambda r: (-r["others"][0][1], -(r["d"]["cjk"] or 0)))
out = os.path.join(BASE, "data", "place_reclass_review.md")
buf = ["弱证据地点人工审查表：现标地名在正文 0 次出现，另一地名反复出现",
       "共 %d 场（已排除人工核定的场次）\n" % len(rows)]
for i, r in enumerate(rows, 1):
    d = r["d"]
    buf.append("%d. %s｜%s｜%s｜%d 字" % (i, d["title"] or r["sc"], d["chapter"], r["sc"], d["cjk"]))
    buf.append("   现标：%s　另有：%s" % (r["cur"],
                                   "、".join("%s×%d" % (k, v) for k, v in r["others"])))
    buf.append("   开场：")
    for seq, sp, t in r["lines"][:3]:
        buf.append("     #%d %s %s" % (seq, sp[:8], t[:110]))
    buf.append("   含地名句：")
    shown = 0
    for seq, sp, t in r["lines"]:
        if any(k in t for k, _ in r["others"]) and shown < 3:
            buf.append("     #%d %s %s" % (seq, sp[:8], t[:110]))
            shown += 1
    buf.append("")
open(out, "w", encoding="utf-8").write("\n".join(buf))
print("候选 %d 场 -> %s" % (len(rows), out))
