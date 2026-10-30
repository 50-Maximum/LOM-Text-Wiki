# -*- coding: utf-8 -*-
"""接入 place_audit2：驻地级标签改「驻地（场所未指明）」，背景证据升级项生效。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

if "PLACE_AUDIT2" not in s:
    anchor = "PLACE_AUDIT = {}"
    add = '''PLACE_AUDIT2 = {}
try:
    _pa2 = os.path.join(BASE, "data", "place_audit2.json")
    if os.path.exists(_pa2):
        PLACE_AUDIT2 = json.load(open(_pa2, encoding="utf-8"))
except Exception:
    PLACE_AUDIT2 = {}

PLACE_AUDIT = {}'''
    assert anchor in s
    s = s.replace(anchor, add, 1)

old = '''        if _v == "doubt":
            return p, "文中提及（存疑）"
        return p, "文中提及"'''
new = '''        if _v == "doubt":
            return p, "文中提及（存疑）"
        _a2 = PLACE_AUDIT2.get(script) or {}
        if _a2.get("label"):
            _lb = _a2["label"].replace("驻地（未细分）", "驻地（场所未指明）")
            return (_a2.get("place") or p), _lb
        return p, "文中提及"'''
assert old in s
s = s.replace(old, new, 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("place_audit2 已接入")
