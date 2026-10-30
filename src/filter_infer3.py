# -*- coding: utf-8 -*-
"""链式推断的正文校验：正文里明写了另一地点且次数更多时，改用正文那个；
两者都没有（推断地点在正文零出现、他地也少）时保留，但标为弱推断。"""
import io, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"

con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
places = [r["name"] for r in con.execute("select name from pages where type='地点'")]
SUF = ("山", "宫", "寺", "镇", "池", "楼", "阁", "院", "城", "门", "庄", "寨", "洞", "峡", "谷", "峰")
EXTRA = {"唐门": ["唐家"], "崆峒山": ["崆峒"], "青城山": ["青城"], "峨嵋山": ["峨嵋", "峨眉"],
         "点苍山": ["点苍"]}


def variants(name):
    base = name.split("-")[-1]
    out = {name, base}
    for suf in SUF:
        if base.endswith(suf) and len(base) - len(suf) >= 2:
            out.add(base[: -len(suf)])
    out.update(EXTRA.get(base, []))
    return [x for x in out if len(x) >= 2]


CANON = {p: variants(p) for p in places}
VAR2NAME = {}
for nm, vs in CANON.items():
    for v in vs:
        VAR2NAME.setdefault(v, nm)

p = os.path.join(BASE, "data", "place_infer3.json")
D = json.load(open(p, encoding="utf-8"))
changed = dropped = 0
for sc, rec in list(D.items()):
    rows = list(con.execute("select text from lines where script=?", (sc,)))
    text = "\n".join((r["text"] or "") for r in rows)
    if not text.strip():
        D.pop(sc)
        dropped += 1
        continue
    cnt = collections.Counter()
    t = text
    for nm, vs in sorted(CANON.items(), key=lambda x: -len(x[0])):
        for v in vs:
            n = t.count(v)
            if n:
                cnt[nm] += n
                t = t.replace(v, "\u0000")
    cur = VAR2NAME.get(rec["place"], rec["place"])
    cur_n = cnt.get(cur, 0)
    best = cnt.most_common(1)[0] if cnt else (None, 0)
    if best[0] and best[1] >= 2 and best[1] > cur_n:
        rec["place"] = best[0]
        rec["src"] = "正文线索（推断）"
        rec["why"] = "正文出现「%s」%d 次，多于原推断" % (best[0], best[1])
        changed += 1
    elif cur_n == 0 and best[1] >= 1:
        D.pop(sc)
        dropped += 1
        continue
    rec["hit"] = cur_n
json.dump(D, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("保留 %d 条；按正文改判 %d 条；剔除 %d 条" % (len(D), changed, dropped))
print("按依据:", collections.Counter(v["src"] for v in D.values()).most_common())
