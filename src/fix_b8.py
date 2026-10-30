# -*- coding: utf-8 -*-
"""第 8 批收尾：补腾云山/福建区域、新增地点类型改用统一判定。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"

p = os.path.join(BASE, "data", "place_edits.json")
E = json.load(open(p, encoding="utf-8"))
E.setdefault("region", {}).update({"腾云山": "荆湖", "福建": "闽越"})
json.dump(E, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("区域补充：腾云山→荆湖，福建→闽越")

S = os.path.join(BASE, "src", "build_wiki2.py")
s = open(S, encoding="utf-8").read()
old = '_region_of(_nm3), "村镇乡野"))'
new = '_region_of(_nm3), _place_type2(_nm3, _lead3, _par3)))'
if old in s:
    s = s.replace(old, new, 1)
    open(S, "w", encoding="utf-8").write(s)
    print("新增地点改用 _place_type2")
else:
    print("未找到硬编码类型（可能已改）")
