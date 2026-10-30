# -*- coding: utf-8 -*-
"""统计地点归属覆盖率（按依据），并抽样看编号推断的场次。"""
import io, json, re, sqlite3, sys, collections, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

by_ev = collections.Counter()
samples = []
total = 0
for r in c.execute("select slug, sections from pages where type='场景'"):
    total += 1
    txt = ""
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息" and s.get("html"):
            txt = s["html"]
    m = re.search(r"地点：([^（(]+)（依据：([^）]+)）", txt)
    if m:
        by_ev[m.group(2)] += 1
        if m.group(2) == "编号规律（推断）":
            samples.append((r["slug"], m.group(1)))
    else:
        by_ev["（无地点）"] += 1

print("场景页合计:", total)
for k, v in by_ev.most_common():
    print("   %-14s %d" % (k, v))
print("\n抽样（编号推断）:")
random.seed(7)
for slug, pl in random.sample(samples, min(8, len(samples))):
    nm = c.execute("select name from pages where slug=?", (slug,)).fetchone()
    print("   %-28s → %-12s %s" % (slug.replace("场景/", ""), pl, nm["name"] if nm else ""))
