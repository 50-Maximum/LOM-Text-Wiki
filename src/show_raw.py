# -*- coding: utf-8 -*-
"""看几个 0 句场景的原始脚本，判断能否据动作起名。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAW = r"D:\LegendOfMortal Wiki\data\raw\scripts"
for sc in ["S0020_02_break_start_01", "S0208_04", "S2200_03", "S0502_01", "S0022_01_01"]:
    p = os.path.join(RAW, sc + ".txt")
    if not os.path.exists(p):
        print(sc, "无原始文件")
        continue
    t = open(p, encoding="utf-8", errors="ignore").read()
    print("\n===== %s (%d 字节)\n%s" % (sc, len(t), t[:700]))
