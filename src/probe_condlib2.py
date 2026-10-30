# -*- coding: utf-8 -*-
"""看 conditions.json 的结构，弄清 Ch_6_7_1_004 / M60015_01 这类键是什么意思。"""
import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"E:\Game\steamapps\common\LegendOfMortal\BepInEx\plugins\LOMAssistant\StoryReview\conditions.json"
d = json.load(open(P, encoding="utf-8"))
print("顶层类型:", type(d).__name__)
if isinstance(d, dict):
    print("顶层键:", list(d)[:12])
    for k in list(d)[:3]:
        print("\n--", k, "->", json.dumps(d[k], ensure_ascii=False)[:400])
elif isinstance(d, list):
    print("条数:", len(d))
    for x in d[:3]:
        print(json.dumps(x, ensure_ascii=False)[:400])
