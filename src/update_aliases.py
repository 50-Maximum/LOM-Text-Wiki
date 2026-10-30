# -*- coding: utf-8 -*-
"""并入角色别称：魏招弟/魏小菊/魏大才女/小魏掌门/玄功魏掌门→魏菊；颜师兄/飞天护法→颜疆；飞天掌门→火龙仙君。"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
fp = r"D:\LegendOfMortal Wiki\data\chars_fix.json"
d = json.load(open(fp, encoding="utf-8"))
m = d.setdefault("merge", {})
m.update({
 "魏招弟": "魏菊",
 "魏小菊": "魏菊",
 "魏大才女": "魏菊",
 "小魏掌门": "魏菊",
 "玄功魏掌门": "魏菊",
 "颜师兄": "颜疆",
 "飞天护法": "颜疆",
 "飞天掌门": "火龙仙君",
})
json.dump(d, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("别名并入完成，merge 共", len(m), "条")
