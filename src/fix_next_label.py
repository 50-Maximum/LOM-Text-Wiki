# -*- coding: utf-8 -*-
"""「接下来」标签细化：Combat/Battle → 战斗；Free → 养成地图。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

old = '''            elif _ty in ("main", "branch", "story", "travel", "temp"):'''
new = '''            elif _ty == "scene" and (_dst.startswith("Combat") or _dst.startswith("Battle")):
                _lab = "战斗：" + _dst
            elif _dst == "Free":
                _lab = "回养成地图（自由行动）"
            elif _ty in ("main", "branch", "story", "travel", "temp", "scene"):'''
assert old in s
s = s.replace(old, new, 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("标签已细化")
