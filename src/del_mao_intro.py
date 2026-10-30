# -*- coding: utf-8 -*-
"""删掉错误的 毛二壮 导语（并义后不应再有独立页）。"""
import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\intros_char.json"
d = json.load(open(p, encoding="utf-8"))
for k in ["人物/毛二壮", "毛二壮"]:
    if k in d:
        d.pop(k)
        print("已删除导语键", k)
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("剩余键", len(d))
