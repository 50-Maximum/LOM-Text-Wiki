# -*- coding: utf-8 -*-
"""把地点复核结果接进 place_of：在场升为「正文在场」，存疑标注，他处清空。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

if "PLACE_AUDIT" not in s:
    anchor = "PLACE_INFER6 = {}"
    i = s.find(anchor)
    j = s.find("\n", s.find("except Exception:", i))
    j = s.find("\n", j + 1) + 1
    s = s[:j] + '''
PLACE_AUDIT = {}
try:
    _pap = os.path.join(BASE, "data", "place_audit.json")
    if os.path.exists(_pap):
        PLACE_AUDIT = json.load(open(_pap, encoding="utf-8"))
except Exception:
    PLACE_AUDIT = {}
''' + s[j:]

old = '''    if p:
        return p, "文中提及"
    return "", ""'''
new = '''    if p:
        _au = PLACE_AUDIT.get(script) or {}
        _v = _au.get("verdict")
        if _v == "here":
            return p, "正文在场"
        if _v == "away":
            return "", "证据不足（原文说的是他处）"
        if _v == "doubt":
            return p, "文中提及（存疑）"
        return p, "文中提及"
    return "", ""'''
assert old in s
s = s.replace(old, new, 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("place_of 已接入复核结果")
