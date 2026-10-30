# -*- coding: utf-8 -*-
"""exit+ 选项统一显示为「结束对话」（覆盖先前被通用表匹配写进的原文）。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_branch_tree.py"
s = open(P, encoding="utf-8").read()

old = '''            if _kind == "exit":
                menu_tabs[_nm].setdefault(_ix, "结束对话")
                continue'''
new = '''            if _kind == "exit":
                menu_tabs[_nm][_ix] = "结束对话"
                continue'''
assert old in s
s = s.replace(old, new, 1)

# 通用清理：残留 exit+ 串
s = s.replace('''def clean_opt(t):''', '''def clean_opt(t):
    t0 = (t or "").strip()
    if t0.lower().startswith("exit+"):
        return "结束对话"''', 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("exit 文案已统一")
