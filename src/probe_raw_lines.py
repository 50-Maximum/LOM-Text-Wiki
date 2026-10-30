# -*- coding: utf-8 -*-
"""看原始脚本的真实行结构，确认能否按行解析。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\raw\scripts\ch6_7_1.txt"
raw = open(p, encoding="utf-8-sig", errors="replace").read()
lines = raw.split("\n")
print("字符", len(raw), "行", len(lines))
for ln in lines[:12]:
    print(repr(ln[:140]))
print("...")
import re
for i, ln in enumerate(lines):
    if "SetNextScript" in ln or "ChangeScene" in ln:
        print(i, repr(ln[:160]))
        if i > 0 and sum(1 for _ in [1]) and i > 2000:
            break
