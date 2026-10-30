# -*- coding: utf-8 -*-
"""收紧正文地名词判定：要求多次命中，或首句/旁白里带方位动词，降低误判。"""
import io, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
D = os.path.join(BASE, "data")
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

scenes = {r[0] for r in con.execute("select script from scenes")}
have = set()
for f in ["place_manual.json", "place_override.json", "scene_place_infer.json",
          "place_logic.json", "place_infer2.json", "place_infer3.json",
          "place_infer4.json", "place_infer5.json"]:
    p = os.path.join(D, f)
    if os.path.exists(p):
        have |= set(json.load(open(p, encoding="utf-8")).keys())

rows = collections.defaultdict(list)
for r in con.execute("select script,seq,text,speaker from lines order by script,seq"):
    if r["script"] in scenes:
        rows[r["script"]].append((r["seq"], r["text"] or "", r["speaker"] or ""))

CUE = re.compile(r"(在|来到|来到这|走进|进入|回到|经过|途经|抵达|登上|穿过|守住|待在|留在|往|赶去|前往)"
                 r"[^。！？]{0,6}$")

out = {}
for sc, ls in rows.items():
    if sc in have:
        continue
    hits = collections.Counter()
    where = {}
    for i, (seq, tx, sp) in enumerate(ls):
        for al, p in ALIAS.items():
            if al not in tx:
                continue
            hits[p] += tx.count(al)
            if p not in where:
                where[p] = (i, sp, tx)
    if not hits:
        continue
    rank = hits.most_common()
    top, n1 = rank[0]
    if len(rank) > 1 and rank[1][1] == n1:
        continue
    i, sp, tx = where[top]
    al = top.split("-")[-1]
    opening = i < 3
    narr = sp == "旁白"
    cue = bool(re.search(re.escape(al) + r"", tx)) and bool(
        re.search(r"(在|来到|走进|进入|回到|经过|登上|穿过|待在)", tx))
    if not (n1 >= 2 or opening or narr or cue):
        continue
    if n1 == 1 and not (opening or narr):
        continue
    out[sc] = {"place": top, "src": "正文地名（推断）",
               "why": "「%s」出现 %d 次%s" % (al, n1, "，位于开篇" if opening else ("，旁白提及" if narr else "")),
               "hit": n1}

json.dump(out, open(os.path.join(D, "place_infer6.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, sort_keys=True)
print("收紧后可判", len(out), "条")
print(collections.Counter(v["place"] for v in out.values()).most_common(12))
for k in list(out)[:12]:
    print("   %-24s → %-14s %s" % (k, out[k]["place"], out[k]["why"]))
