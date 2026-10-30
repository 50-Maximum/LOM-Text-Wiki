# -*- coding: utf-8 -*-
"""地点复核：对「文中提及」这一档逐场看上下文，分清在场、他处、存疑。

判据：
  在场  地名附近 3 行内出现 你在/来到/走进/踏入/坐在/站在/回到/房内/殿内/堂上/院中/门前
  他处  地名附近出现 去/往/派/叫/吩咐/传话/送信/听说/据说/传闻/若/假如/要是/当年/曾
  其余  存疑（保留原地名，标注存疑）
输出 data/place_audit.json：{script: {place, verdict, hits, note}}
"""
import io, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "scripts")

con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
rows = [dict(r) for r in con.execute(
    "select script, coalesce(place,'') place, coalesce(title,'') title from scenes")]

HERE = ["你在", "你来到", "你走进", "你踏入", "你坐在", "你站在", "你回到", "你望着",
        "众人在", "赵活在", "人在", "房内", "殿内", "堂上", "院中", "门前", "屋内",
        "厅中", "房中", "帐内", "洞中", "林中", "山门", "这里", "此地"]
AWAY = ["去", "往", "派", "叫", "吩咐", "传话", "送信", "听说", "据说", "传闻",
        "若", "假如", "要是", "当年", "曾", "那边", "一带", "之外", "远处"]

def norm(s):
    return (s or "").replace("　", "")

out = {}
stat = collections.Counter()
for r in rows:
    sc, place = r["script"], norm(r["place"])
    if not place:
        continue
    p = os.path.join(RAW, sc + ".txt")
    if not os.path.exists(p):
        continue
    lines = open(p, encoding="utf-8", errors="replace").read().split("\n")
    hit_pos = [i for i, ln in enumerate(lines) if place in ln]
    if not hit_pos:
        continue
    here = away = 0
    for i in hit_pos[:12]:
        lo, hi = max(0, i - 3), min(len(lines), i + 4)
        ctx = norm("".join(lines[lo:hi]))
        if any(w in ctx for w in HERE):
            here += 1
        if any(w in ctx for w in AWAY):
            away += 1
    if here and not away:
        verdict, src = "here", "正文在场"
    elif away and not here:
        verdict, src = "away", "证据不足（原文说的是他处）"
    else:
        verdict, src = "doubt", "文中提及（存疑）"
    stat[verdict] += 1
    out[sc] = {"place": place, "verdict": verdict, "here": here, "away": away, "src": src}

json.dump(out, open(os.path.join(BASE, "data", "place_audit.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)
print("复核 %d 场；在场 %d ／ 他处 %d ／ 存疑 %d" % (len(out), stat["here"], stat["away"], stat["doubt"]))
for sc, v in list(out.items())[:6]:
    print("  %-26s %-8s 在场%d 他处%d" % (sc, v["place"], v["here"], v["away"]))
