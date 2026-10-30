# -*- coding: utf-8 -*-
"""按剧情阶段看地点分布，找出「靠词频猜出来的地点」是否与阶段冲突。"""
import io, sys, json, sqlite3, collections, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(B, "data", "wiki.db")).cursor()

arcs = json.load(open(os.path.join(B, "data", "arcs.json"), encoding="utf-8"))
print("arcs.json 键:", list(arcs.keys())[:8])

rows = list(c.execute("select script,coalesce(place,''),coalesce(chapter,'') from scenes"))
print("场景 %d" % len(rows))
print("\n=== chapter 取值")
for k, v in collections.Counter(r[2] for r in rows).most_common(20):
    print("  %-24s %d" % (k or "（空）", v))

print("\n=== place 取值")
for k, v in collections.Counter(r[1] for r in rows).most_common(15):
    print("  %-18s %d" % (k or "（空）", v))

print("\n=== 各阶段的地点分布（前 6）")
by = collections.defaultdict(collections.Counter)
for sc, p, ch in rows:
    by[ch or "（空）"][p or "（空）"] += 1
for ch, cnt in sorted(by.items(), key=lambda x: -sum(x[1].values())):
    print(" ", ch, dict(cnt.most_common(5)))
