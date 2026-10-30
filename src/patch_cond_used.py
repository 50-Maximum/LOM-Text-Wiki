# -*- coding: utf-8 -*-
"""条件条目反查改用 cond_used.json（扫全量脚本），覆盖 Switch 直接引用。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

if "COND_USED" not in s:
    a = "COND_LIB = {}"
    i = s.find(a)
    j = s.find("\n", s.find("except Exception:", i))
    j = s.find("\n", j + 1) + 1
    s = s[:j] + '''
COND_USED = {}
try:
    _cup = os.path.join(BASE, "data", "cond_used.json")
    if os.path.exists(_cup):
        COND_USED = json.load(open(_cup, encoding="utf-8"))
except Exception:
    COND_USED = {}
''' + s[j:]

old = "_COND_USED = {}\ntry:"
if "COND_USED.items()" not in s:
    assert old in s
    s = s.replace(old, '''_COND_USED = {k: set(v) for k, v in COND_USED.items()}
try:''', 1)
    print("反查已接入 cond_used.json")

open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("syntax ok")
