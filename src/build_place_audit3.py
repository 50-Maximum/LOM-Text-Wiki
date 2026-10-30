# -*- coding: utf-8 -*-
"""地点复核 v3：按「地名前后动词」判在场/他处，避免单个 去/往 误杀。

在场：在{地}、到{地}、回{地}、进{地}、来到{地}、{地}内/中/上/前、走过{地}
他处：去{地}、前往{地}、赶往{地}、离开{地}、派人去、叫他去{地}、听说{地}、据说{地}
"""
import io, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "scripts")
con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
rows = [dict(r) for r in con.execute("select script, coalesce(place,'') place from scenes")]

out, stat = {}, collections.Counter()
for r in rows:
    sc, place = r["script"], (r["place"] or "").strip()
    if not place:
        continue
    p = os.path.join(RAW, sc + ".txt")
    if not os.path.exists(p):
        continue
    text = open(p, encoding="utf-8", errors="replace").read()
    if place not in text:
        continue
    here_pats = ["在" + place, "到" + place, "回" + place, "进" + place, "来到" + place,
                 place + "内", place + "中", place + "上", place + "前", "走过" + place]
    away_pats = ["去" + place, "前往" + place, "赶往" + place, "离开" + place,
                 "听说" + place, "据说" + place, "传闻" + place, "前往", "赶赴" + place]
    h = sum(text.count(x) for x in here_pats)
    a = sum(text.count(x) for x in away_pats[:7])
    if h and h >= a:
        verdict = "here"
    elif a >= 2 and h == 0:
        verdict = "away"
    else:
        verdict = "doubt"
    stat[verdict] += 1
    out[sc] = {"place": place, "verdict": verdict, "here": h, "away": a}

json.dump(out, open(os.path.join(BASE, "data", "place_audit.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)
print("复核 %d 场；在场 %d ／ 他处 %d ／ 存疑 %d" % (len(out), stat["here"], stat["away"], stat["doubt"]))
for sc, v in list(out.items())[:10]:
    print("  %-26s %-8s 在场%d 他处%d %s" % (sc, v["place"], v["here"], v["away"], v["verdict"]))
