# -*- coding: utf-8 -*-
"""选项行补上说明（为什么没有去向、战斗后续接等）。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")
old = """                if _o.get("effects"):
                    _note += "　影响：" + "、".join(_o["effects"])"""
new = """                if _o.get("effects"):
                    _note += "　影响：" + "、".join(_o["effects"])
                if _o.get("note"):
                    _note += "　" + _o["note"]"""
if old in s and '_o["note"]' not in s:
    s = s.replace(old, new, 1)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("选项说明已接入")
else:
    print("已接入或未找到锚点")
