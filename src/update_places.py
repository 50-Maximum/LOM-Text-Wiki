# -*- coding: utf-8 -*-
"""地点层级修正：唐门归入眉山；清掉指向已删地区页的上级。"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
fp = r"D:\LegendOfMortal Wiki\data\places_fix.json"
d = json.load(open(fp, encoding="utf-8"))
p = d.setdefault("parent", {})
p["唐门"] = "眉山"
for k in ("风雨山", "锦香宫", "丐帮-大义分舵", "丐帮-眉山分舵", "丐帮-大智分舵"):
    p.pop(k, None)
json.dump(d, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("地点层级已更新：唐门→眉山，清除失效上级", len(p), "条")
