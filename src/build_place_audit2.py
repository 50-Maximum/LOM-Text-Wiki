# -*- coding: utf-8 -*-
"""地点复核 v2：只看地名所在的那一句（前一句作旁白补充），避免整窗误判。"""
import io, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "scripts")

con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
rows = [dict(r) for r in con.execute(
    "select script, coalesce(place,'') place from scenes")]

SENT = re.compile(r"[^。！？!?；;\n]{0,80}")
HERE = ["你在", "你来到", "你走进", "你踏入", "你坐在", "你站在", "你回到", "你望着",
        "众人在", "赵活在", "回到", "走进", "踏入", "走入", "身在", "人在",
        "房内", "殿内", "堂上", "院中", "门前", "屋内", "厅中", "房中", "帐内", "洞中", "林中"]
AWAY = ["去", "往", "派", "叫", "吩咐", "传话", "送信", "听说", "据说", "传闻",
        "若", "假如", "要是", "当年", "曾说", "那边", "一带"]


def sentences_of(line):
    return [s for s in re.split(r"[。！？!?；;]", line) if s.strip()]


out = {}
stat = collections.Counter()
for r in rows:
    sc, place = r["script"], (r["place"] or "").strip()
    if not place:
        continue
    p = os.path.join(RAW, sc + ".txt")
    if not os.path.exists(p):
        continue
    lines = open(p, encoding="utf-8", errors="replace").read().split("\n")
    hits = [i for i, ln in enumerate(lines) if place in ln]
    if not hits:
        continue
    here = away = 0
    for i in hits[:10]:
        prev = lines[i - 1] if i > 0 else ""
        for s in sentences_of(lines[i]):
            if place not in s:
                continue
            ctx = prev + "。" + s
            h = any(w in s for w in HERE) or any(w in prev for w in ("你在", "回到", "走进", "来到"))
            a = any(w in s.replace(place, "") for w in AWAY)
            if h and not a:
                here += 1
            elif a and not h:
                away += 1
    if here and here >= away:
        verdict = "here"
    elif away and not here:
        verdict = "away"
    else:
        verdict = "doubt"
    stat[verdict] += 1
    out[sc] = {"place": place, "verdict": verdict, "here": here, "away": away}

json.dump(out, open(os.path.join(BASE, "data", "place_audit.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)
print("复核 %d 场；在场 %d ／ 他处 %d ／ 存疑 %d" % (len(out), stat["here"], stat["away"], stat["doubt"]))
for sc, v in list(out.items())[:8]:
    print("  %-26s %-8s 在场%d 他处%d %s" % (sc, v["place"], v["here"], v["away"], v["verdict"]))
