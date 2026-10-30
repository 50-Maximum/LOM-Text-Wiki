# -*- coding: utf-8 -*-
"""诊断 758 条指向空页的链接：那些脚本是什么。"""
import io, json, os, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row
pages = {r[0] for r in c.execute("select slug from pages where type='场景'")}
scenes = {r[0] for r in c.execute("select script from scenes")}
raw = {f[:-4] for f in os.listdir(os.path.join(BASE, "data", "raw", "scripts")) if f.endswith(".txt")}

miss = collections.Counter()
where = collections.Counter()
for r in c.execute("select slug,sections from pages where type='场景'"):
    for s in json.loads(r["sections"] or "[]"):
        for x in (s.get("rows") or []):
            sc = x.get("script") or ""
            if sc and ("场景/" + sc) not in pages:
                miss[sc] += 1
                where[s.get("h")] += 1
print("缺失目标 %d 个，出现 %d 次" % (len(miss), sum(miss.values())))
print("所在栏目:", where.most_common())
in_scenes = sum(1 for sc in miss if sc in scenes)
in_raw = sum(1 for sc in miss if sc in raw)
print("在 scenes 表里:", in_scenes, "在 raw 里有文件:", in_raw)
print("\n样例:")
for sc, n in miss.most_common(12):
    print("   %-30s ×%-3d scenes=%s raw=%s" % (sc, n, sc in scenes, sc in raw))
