# -*- coding: utf-8 -*-
"""统计人物前缀分布，找出不在势力页里的前缀。"""
import io, json, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
fac = set(r["name"] for r in c.execute("select name from pages where type='势力'"))
cnt = collections.Counter()
for r in c.execute("select name from pages where type='人物'"):
    nm = r["name"]
    p = nm.split("·")[0] if "·" in nm else "（无前缀）"
    cnt[p] += 1
print("势力页 %d 个，人物前缀 %d 种" % (len(fac), len(cnt)))
print("\n-- 前缀不在势力页里 --")
for p, n in cnt.most_common():
    if p not in fac:
        print("   %-12s %3d" % (p, n))
print("\n-- 势力页里没有人物的 --")
for f in sorted(fac):
    if f not in cnt:
        print("   ", f)
print("\n合计人物", sum(cnt.values()))
