# -*- coding: utf-8 -*-
"""看占位选项在剧本里的原始写法，找它真正的文案来源。"""
import io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAW = r"D:\LegendOfMortal Wiki\data\raw\scripts"
p = os.path.join(RAW, "S0003_01_02.txt")
raw = open(p, encoding="utf-8-sig", errors="replace").read()
lines = raw.split("\n")
print("行数", len(lines))
for i, ln in enumerate(lines):
    if re.search(r"choose|choice|option|O_", ln, re.I):
        for j in range(max(0, i - 2), min(len(lines), i + 8)):
            print("%5d %s" % (j, lines[j][:150]))
        print("-----")
        if i > 400:
            break
