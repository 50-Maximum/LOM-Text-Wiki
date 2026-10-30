# -*- coding: utf-8 -*-
"""修 SCENES_BY_PLACE：逐场 try，单场异常不再清空整张表。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(S, encoding="utf-8").read()
old = """SCENES_BY_PLACE = {}
try:
    for _s7 in scenes:
        _p7, _e7 = place_of(_s7)
        if _p7:
            SCENES_BY_PLACE.setdefault(_p7, []).append(_s7)
except Exception:
    SCENES_BY_PLACE = {}"""
new = """SCENES_BY_PLACE = {}
for _s7 in list(scenes):
    try:
        _p7, _e7 = place_of(_s7)
    except Exception:
        continue
    if _p7:
        SCENES_BY_PLACE.setdefault(_p7, []).append(_s7)
print("地点-场景索引", len(SCENES_BY_PLACE), "个地点 /",
      sum(len(v) for v in SCENES_BY_PLACE.values()), "场")"""
assert old in s, "建表块未找到"
s = s.replace(old, new, 1)
open(S, "w", encoding="utf-8").write(s)
print("已改为逐场容错")
