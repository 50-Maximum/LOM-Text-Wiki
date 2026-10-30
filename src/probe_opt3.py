# -*- coding: utf-8 -*-
"""看剩余 66 个占位选项的原始写法。"""
import io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAW = r"D:\LegendOfMortal Wiki\data\raw\scripts"
for sc in ["S0014_01_05_break_start_01", "S0208_04_break_start_01"]:
    p = os.path.join(RAW, sc + ".txt")
    if not os.path.exists(p):
        print(sc, "无文件"); continue
    txt = open(p, encoding="utf-8", errors="replace").read()
    lines = txt.split("\n")
    print("\n=====", sc, len(lines), "行")
    for i, ln in enumerate(lines):
        if re.search(r'\[\d+\]\s*=|choose|menudialog|option', ln):
            print("%4d %s" % (i, ln[:140]))
