# -*- coding: utf-8 -*-
"""修正边类型：if 里的 SetNextScript 属于分支（branch），不是主线。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_scene_graph.py"
s = open(P, encoding="utf-8").read()
old = '''        etype = KIND.get(fn, "main")
        if not cond:
            etype = "main" if fn == "SetNextScript" else etype'''
new = '''        etype = KIND.get(fn, "main")
        if fn == "SetNextScript":
            etype = "branch" if cond else "main"'''
assert old in s
s = s.replace(old, new, 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("已修正边类型规则")
