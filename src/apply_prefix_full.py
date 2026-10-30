# -*- coding: utf-8 -*-
"""门派前缀统一成「XX派」全称；并按参考 wiki 补两条归属。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\chars_prefix.json"
d = json.load(open(p, encoding="utf-8"))
MAP = {"青城": "青城派", "崆峒": "崆峒派", "点苍": "点苍派", "峨嵋": "峨嵋派",
       "全真": "全真派", "岭南": "岭南派", "雪山": "雪山派", "华山": "华山派",
       "飞天": "飞天门", "官方": "朝廷"}
for k, v in list(d.items()):
    if v in MAP:
        d[k] = MAP[v]
d["晁和"] = "岭南派"
d["火闪电"] = "崆峒派"
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
from collections import Counter
print("前缀覆盖", len(d), Counter(d.values()).most_common(12))
