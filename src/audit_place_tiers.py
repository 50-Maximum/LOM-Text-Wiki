# -*- coding: utf-8 -*-
"""统计场景页的地点判据分布（依据字段），找出最该复核的档位。"""
import io, json, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
cnt = collections.Counter()
noplace = 0
total = 0
for r in c.execute("select slug,sections from pages where type='场景'"):
    total += 1
    loc = ""
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息":
            loc = s.get("html") or ""
            break
    if "地点：" not in loc:
        noplace += 1
        continue
    m = re.search(r"（依据：([^）]+)）", loc)
    cnt[m.group(1) if m else "(无依据)"] += 1

lines = ["场景总数 %d，无地点 %d" % (total, noplace), ""]
for k, v in cnt.most_common():
    lines.append("%-24s %5d" % (k, v))
open(r"D:\LegendOfMortal Wiki\data\_place_tiers.txt", "w", encoding="utf-8").write("\n".join(lines))
print("ok")
