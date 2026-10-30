# -*- coding: utf-8 -*-
"""S0014_01_06 被投票拉到江陵围城，实际是支线（崆峒留学期间的护人场面），改回不限时间。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
p = os.path.join(B, "arcs.json")
d = json.load(open(p, encoding="utf-8"))
d.setdefault("scene", {})["S0014_01_06"] = "不限时间"
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("S0014_01_06 → 不限时间")
