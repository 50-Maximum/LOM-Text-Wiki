# -*- coding: utf-8 -*-
"""接入 place_infer4.json（事件链顺延），优先级排在编号规律与链式推断之后。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(S, encoding="utf-8").read()

if "PLACE_INFER4" not in s:
    anchor = 'PLACE_INFER3 = {}'
    i = s.find(anchor)
    assert i > 0
    # 找到 PLACE_INFER3 载入块结尾
    j = s.find("PLACE_INFER3 = {}", s.find("except Exception:", i))
    j = s.find("\n", j) + 1
    add = '''
PLACE_INFER4 = {}
try:
    _pi4 = os.path.join(BASE, "data", "place_infer4.json")
    if os.path.exists(_pi4):
        PLACE_INFER4 = json.load(open(_pi4, encoding="utf-8"))
except Exception:
    PLACE_INFER4 = {}
'''
    s = s[:j] + add + s[j:]
    print("已加载 PLACE_INFER4")

if "PLACE_INFER4.get(script)" not in s:
    tail = '    _i3 = PLACE_INFER3.get(script) or {}'
    assert tail in s
    ins = '''    _i4 = PLACE_INFER4.get(script) or {}
    if _i4.get("place"):
        return pcanon(_i4["place"]), (_i4.get("src") or "事件链顺延（推断）")
'''
    s = s.replace(tail, ins + tail, 1)
    print("place_of 已接事件链顺延")

open(S, "w", encoding="utf-8").write(s)
print("done")
