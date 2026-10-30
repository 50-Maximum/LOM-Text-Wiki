# -*- coding: utf-8 -*-
"""汇总属性判定：每个数值在哪些场景被要求到多少。

来源：data/scene_conds.json（场景判定文本）、data/position_events.json（地图事件条件）
输出 data/stats.json：{属性名: [{script, req}, ...]}
"""
import io, sys, os, re, json, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WIKI = r"D:\LegendOfMortal Wiki"
PAT = re.compile(r"^([^\s\d≤≥＜＞=<>]{1,8})\s*([≤≥＜＞=<>]+)\s*(-?\d+)")

CONDS = json.load(open(os.path.join(WIKI, "data", "scene_conds.json"), encoding="utf-8"))
POS = json.load(open(os.path.join(WIKI, "data", "position_events.json"), encoding="utf-8"))

out = collections.defaultdict(list)
seen = set()


def add(stat, req, script):
    k = (stat, req, script)
    if k in seen:
        return
    seen.add(k)
    out[stat].append({"script": script, "req": req})


for sc, items in CONDS.items():
    for it in items:
        t = (it.get("text") or "").strip()
        m = PAT.match(t)
        if m:
            add(m.group(1), t, sc)

for d in POS:
    for tx in (d.get("cond") or []) + [x for r in (d.get("rates") or []) for x in (r.get("cond") or [])]:
        m = PAT.match((tx or "").strip())
        if m:
            add(m.group(1), tx.strip(), "")

stats = {k: v for k, v in out.items() if len(v) >= 5}
json.dump(stats, open(os.path.join(WIKI, "data", "stats.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("属性数（≥5 次判定）:", len(stats))
for k, v in sorted(stats.items(), key=lambda x: -len(x[1]))[:15]:
    reqs = collections.Counter(x["req"] for x in v)
    print("   %-10s %3d 处  常见：%s" % (k, len(v), "、".join(r for r, _ in reqs.most_common(3))))
