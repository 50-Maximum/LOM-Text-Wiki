# -*- coding: utf-8 -*-
"""把 place_infer2.json（编号规律推断）接进 place_of，并给出覆盖率统计。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(S, encoding="utf-8").read()

if "PLACE_INFER2" not in s:
    anchor = 'PE_TYPE = PE.get("type") or {}'
    assert anchor in s
    s = s.replace(anchor, anchor + '''

# 编号规律推断（src/infer_by_id.py 生成）
PLACE_INFER2 = {}
try:
    _pi2 = os.path.join(BASE, "data", "place_infer2.json")
    if os.path.exists(_pi2):
        PLACE_INFER2 = json.load(open(_pi2, encoding="utf-8"))
except Exception:
    PLACE_INFER2 = {}''', 1)
    print("已加载 PLACE_INFER2")

head = '''    lg = PLACE_LOGIC.get(script) or {}
    if lg.get("place"):'''
if "PLACE_INFER2.get(script)" not in s:
    idx = s.find(head)
    assert idx > 0, "place_of 逻辑分支未找到"
    # 找到该分支结束（到 if p: 之前）
    tail = "    if p:\n        return p, \"文中提及\""
    j = s.find(tail, idx)
    assert j > idx
    ins = '''    _i2 = PLACE_INFER2.get(script) or {}
    if _i2.get("place"):
        return pcanon(_i2["place"]), "编号规律（推断）"
'''
    s = s[:j] + ins + s[j:]
    print("place_of 已接编号推断")

open(S, "w", encoding="utf-8").write(s)
print("done")
