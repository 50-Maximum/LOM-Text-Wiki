# -*- coding: utf-8 -*-
"""按五零给的结构重构地点层级：

  川蜀 → 眉山、峨嵋山（峨眉山）、唐门…
  江陵 → 千金方医馆、江陵-南宫大宅
  岳阳 → 锦香宫、风雨山
  锦香宫 → 武英殿、华音阁（子级的子级）
  丐帮-大义分舵：是组织不是地名 → 从地点里删掉
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\data\places_fix.json"
d = json.load(open(P, encoding="utf-8"))
par = d.setdefault("parent", {})
dele = set(d.get("delete") or [])
mer = d.setdefault("merge", {})

NEW_PARENT = {
    "千金方医馆": "江陵",
    "风雨山": "岳阳",
    "锦香宫": "岳阳",
    "眉山": "川蜀",
    "峨嵋山": "川蜀",
    "华音阁": "锦香宫",
    "唐门": "眉山",
    "岷江": "眉山",
    "渡口": "眉山",
}
par.update(NEW_PARENT)
# 峨眉山/峨嵋山统一
mer.setdefault("峨眉山", "峨嵋山")
# 丐帮分舵是组织，不是地名
dele.add("丐帮-大义分舵")
dele.add("丐帮-大智分舵")
dele.add("丐帮-眉山分舵")

d["parent"] = par
d["delete"] = sorted(dele)
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("parent 共 %d 条，本次改动：" % len(par))
for k, v in NEW_PARENT.items():
    print("  %-12s → %s" % (k, v))
print("delete 共 %d 条（新增丐帮分舵 3 个）" % len(dele))
print("merge: 峨眉山 → %s" % mer["峨眉山"])
