# -*- coding: utf-8 -*-
"""无地点场景显式标注：0 句脚本标「转场节点」，有台词但无场所证据标「地点未证」。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

old = '''                     + (f"地点：{pv}" + (f"（依据：{_pv_ev}）" if _pv_ev else "") + "。"
                        if pv else "")}]'''
new = '''                     + (f"地点：{pv}" + (f"（依据：{_pv_ev}）" if _pv_ev else "") + "。"
                        if pv else ("地点：转场节点（本场无台词，不涉及场所）。"
                                    if (sc.get("lines") or 0) <= 0
                                    else "地点：未证（正文未指明具体场所）。"))}]'''
assert old in s
s = s.replace(old, new, 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("无地点标注已接入")
