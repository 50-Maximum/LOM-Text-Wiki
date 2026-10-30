# -*- coding: utf-8 -*-
"""把 scene_time_ref 的年/月字段统一成 REFTIME 解析器要的格式：第X年 / X月。"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\data\scene_time_ref.json"
ref = json.load(open(P, encoding="utf-8"))
fix = 0
for sc, v in ref.items():
    y = v.get("year") or ""
    m = v.get("month") or ""
    ny = y if re.search(r"第[\u4e00-\u9fa5]+年", y) else "第%s年" % y.strip("第年")
    nm = m if re.search(r"[\u4e00-\u9fa5]+月", m) else "%s月" % m.strip("月")
    x = v.get("xun") or ""
    nx = x if x in ("上", "中", "下") else x
    if (ny, nm, nx) != (y, m, x):
        v["year"], v["month"], v["xun"] = ny, nm, nx
        fix += 1
        print("改 %-22s %s %s %s → %s %s %s" % (sc, y, m, x, ny, nm, nx))
json.dump(ref, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n规范 %d 条，共 %d 条" % (fix, len(ref)))
