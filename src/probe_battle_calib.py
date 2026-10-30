# -*- coding: utf-8 -*-
"""读 act3_3_3 / ch2_4_7_2_1 的战斗分支原文，校准胜负判定。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAW = r"D:\LegendOfMortal Wiki\data\raw\scripts"
for sc in ["act3_3_3", "ch2_4_7_2_1", "S0209_01_02"]:
    p = os.path.join(RAW, sc + ".txt")
    t = open(p, encoding="utf-8", errors="ignore").read()
    print("\n=========", sc, len(t))
    print(t[:1200])
