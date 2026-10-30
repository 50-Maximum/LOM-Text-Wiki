# -*- coding: utf-8 -*-
"""看仍有占位选项的脚本原始写法，找出漏掉的表格式。"""
import io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAW = r"D:\LegendOfMortal Wiki\data\raw\scripts"
for sc in ["S0003_02_02_break_01", "S0003_03_break_01"]:
    p = os.path.join(RAW, sc + ".txt")
    if not os.path.exists(p):
        print(sc, "无文件"); continue
    lines = open(p, encoding="utf-8", errors="replace").read().split("\n")
    print("\n=====", sc, len(lines), "行")
    for i, ln in enumerate(lines):
        if re.search(r'\[\d+\]\s*=|choose|choosetimer|menu', ln):
            print("%4d %s" % (i, ln[:130]))
