# -*- coding: utf-8 -*-
"""选项文案清理：去掉 ~ 前缀与 |条件 尾巴。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_branch_tree.py"
s = open(P, encoding="utf-8").read()

old = '''def zh(code):'''
new = '''def clean_opt(t):
    """选项文案清理：去 ~ 前缀、去 |条件 尾巴。"""
    t = (t or "").strip().lstrip("~").strip()
    if "|" in t:
        t = t.split("|", 1)[0].strip()
    return t


def zh(code):'''
assert old in s and "def clean_opt" not in s
s = s.replace(old, new, 1)

s = s.replace('node = {"label": zh(txt) or ("结果%d" % val), "kind": "dice"',
              'node = {"label": clean_opt(zh(txt)) or ("结果%d" % val), "kind": "dice"', 1)
s = s.replace('node = {"label": lab or ("选项%d" % val), "kind": "choose"',
              'node = {"label": clean_opt(lab) or ("选项%d" % val), "kind": "choose"', 1)
s = s.replace('p["options"].append({"idx": i, "text": lab, "cond": ""})',
              'p["options"].append({"idx": i, "text": clean_opt(lab), "cond": ""})', 1)
s = s.replace('p["options"].append({"idx": i, "text": zh(txt), "cond": cond,',
              'p["options"].append({"idx": i, "text": clean_opt(zh(txt)), "cond": cond,', 1)

open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("选项文案已清理")
