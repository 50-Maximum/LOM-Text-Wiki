# -*- coding: utf-8 -*-
"""核验无地点标注：统计两类标签各多少场。"""
import io, json, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
cnt = collections.Counter()
samples = collections.defaultdict(list)
for r in c.execute("select slug,sections from pages where type='场景'"):
    t = ""
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息":
            t = s.get("html") or ""
            break
    if "转场节点" in t:
        cnt["转场节点"] += 1
        if len(samples["转场节点"]) < 3:
            samples["转场节点"].append(r["slug"])
    elif "地点：未证" in t:
        cnt["地点：未证"] += 1
        if len(samples["地点：未证"]) < 3:
            samples["地点：未证"].append(r["slug"])
    elif "地点：" in t:
        cnt["有地点"] += 1
print(dict(cnt))
for k, v in samples.items():
    print(k, v)

