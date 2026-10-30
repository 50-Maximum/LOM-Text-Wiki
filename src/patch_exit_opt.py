# -*- coding: utf-8 -*-
"""talk 表里的 exit 项不再跳过，标成「结束对话」；空槽位标「（无文案）」。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_branch_tree.py"
s = open(P, encoding="utf-8").read()

old = '''            if _kind == "exit":
                continue          # 结束对话的入口，不算选项'''
new = '''            if _kind == "exit":
                menu_tabs[_nm].setdefault(_ix, "结束对话")
                continue'''
assert old in s
s = s.replace(old, new, 1)

s = s.replace('node = {"label": clean_opt(lab) or ("选项%d" % val), "kind": "choose"',
              'node = {"label": clean_opt(lab) or ("（无文案槽位 %d）" % val), "kind": "choose"', 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("exit 项已标注")
