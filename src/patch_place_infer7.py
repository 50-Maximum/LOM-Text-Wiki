# -*- coding: utf-8 -*-
"""接入 place_infer7（承前场 / 背景资源补齐无地点场景）。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

if "PLACE_INFER7" not in s:
    anchor = '''    _i2 = PLACE_INFER2.get(script) or {}
    if _i2.get("place"):
        return pcanon(_i2["place"]), "编号规律（推断）"'''
    add = anchor + '''
    _i7 = PLACE_INFER7.get(script) or {}
    if _i7.get("place"):
        return pcanon(_i7["place"]), (_i7.get("src") or "承前场（推断）")'''
    assert anchor in s
    s = s.replace(anchor, add, 1)

    anchor2 = "PLACE_AUDIT2 = {}"
    add2 = '''PLACE_INFER7 = {}
try:
    _p7 = os.path.join(BASE, "data", "place_infer7.json")
    if os.path.exists(_p7):
        PLACE_INFER7 = json.load(open(_p7, encoding="utf-8"))
except Exception:
    PLACE_INFER7 = {}

PLACE_AUDIT2 = {}'''
    assert anchor2 in s
    s = s.replace(anchor2, add2, 1)

open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("place_infer7 已接入")
