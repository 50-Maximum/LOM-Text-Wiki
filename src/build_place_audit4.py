# -*- coding: utf-8 -*-
"""地点档位复核 v4：
1) 「文中提及」里地点只到门派级的，改标「驻地（未细分）」；
2) 同章节 + 同背景的其它场景若 ≥80% 指向同一具体场所（≥3 场），据此升级为「背景资源（推断）」。
输出 data/place_audit2.json 与统计。
"""
import io, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row
bg = json.load(open(os.path.join(BASE, "data", "scene_bg.json"), encoding="utf-8"))
ch = {r[0]: (r[1] or "") for r in c.execute("select script,chapter from scenes")}

def info(sections):
    for s in json.loads(sections or "[]"):
        if s.get("h") == "场景信息":
            return s.get("html") or ""
    return ""

scene = {}
for r in c.execute("select slug,sections from pages where type='场景'"):
    sc = r["slug"][len("场景/"):] if r["slug"].startswith("场景/") else r["slug"]
    t = info(r["sections"])
    if "地点：" not in t:
        continue
    m = re.search(r"地点：([^（。]+)（依据：([^）]+)）", t)
    if m:
        scene[sc] = (m.group(1).strip(), m.group(2).strip())

mention = {sc: v for sc, v in scene.items() if v[1] == "文中提及"}
print("文中提及", len(mention))

# 章节+背景 共识表：只统计已有具体场所（带 - ）的场景
cons = collections.defaultdict(collections.Counter)
for sc, (p, tier) in scene.items():
    if "-" not in p:
        continue
    if tier.startswith(("文中提及", "存疑")):
        continue
    b = (bg.get(sc) or [""])[0]
    if not b:
        continue
    cons[(ch.get(sc, ""), b)][p] += 1

out = {}
up = relabel = 0
for sc, (p, tier) in mention.items():
    if "-" in p:
        out[sc] = {"place": p, "verdict": "doubt", "label": "文中提及（存疑）"}
        relabel += 1
        continue
    b = (bg.get(sc) or [""])[0]
    cnt = cons.get((ch.get(sc, ""), b)) or collections.Counter()
    tot = sum(cnt.values())
    if tot >= 3 and cnt:
        top, n = cnt.most_common(1)[0]
        if n / tot >= 0.8:
            out[sc] = {"place": top, "verdict": "here", "label": "背景资源（推断）", "why": "%s/%s %d/%d" % (ch.get(sc, ""), b, n, tot)}
            up += 1
            continue
    out[sc] = {"place": p, "verdict": "here", "label": "驻地（未细分）"}

json.dump(out, open(os.path.join(BASE, "data", "place_audit2.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)
print("升级为具体场所 %d ／ 具体场所但无正文证据 %d ／ 留在驻地级 %d" % (up, relabel, len(out) - up - relabel))
for sc, v in list(out.items())[:8]:
    print("   %-28s %-16s %s" % (sc, v["place"], v["label"]))
