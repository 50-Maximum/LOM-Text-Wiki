# -*- coding: utf-8 -*-
"""把咖啡伴侣的判定库整理成条件条目数据：data/cond_lib.json

Switches: 多路判定（按结果序号 1、2、3… 分支），每个结果给一条可读条件
Conditions: 单条条件表达式
"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
SRC = r"E:\Game\steamapps\common\LegendOfMortal\BepInEx\plugins\LOMAssistant\StoryReview\conditions.json"
OUT = r"D:\LegendOfMortal Wiki\data\cond_lib.json"

d = json.load(open(SRC, encoding="utf-8"))
SW = d.get("Switches") or {}
CD = d.get("Conditions") or {}

lib = {}
for k, v in SW.items():
    if isinstance(v, list):
        attrs = [str(x) for x in v]
    else:
        attrs = [str(v)]
    lib[k] = {"kind": "switch", "attrs": attrs}
for k, v in CD.items():
    if k in lib:
        # 同名时把表达式并进去
        lib[k]["expr"] = str(v)
        continue
    lib[k] = {"kind": "cond", "attrs": [str(v)]}

json.dump(lib, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
print("条件条目:", len(lib), "（switch %d / cond %d）" % (len(SW), len(CD)))
print("版本:", d.get("Version"))
for k in ["Ch_6_7_1_004", "Ch_6_7_1_005", "Ch_6_7_1_006", "M60015_01", "S_Beh_LT_60"]:
    print("  %-16s %s" % (k, json.dumps(lib.get(k), ensure_ascii=False)[:150]))
