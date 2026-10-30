# -*- coding: utf-8 -*-
"""读 S0209_01_02 的战斗结果分支原文，确认真实的胜负方向。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = os.path.join(r"D:\LegendOfMortal Wiki\data\raw\scripts", "S0209_01_02.txt")
t = open(p, encoding="utf-8", errors="ignore").read()
i = t.find("Combat_Result")
print("长度", len(t), "位置", i)
print(t[max(0, i - 200): i + 1600])
