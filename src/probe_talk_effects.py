# -*- coding: utf-8 -*-
"""看 talk 选项体里有哪些「效果」调用（旗标/数值/好感）。"""
import io, sys, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
f = r"D:\LegendOfMortal Wiki\data\raw\scripts\ch6_6_2_break_start_01.txt"
lines = open(f, encoding="utf-8", errors="replace").read().split("\n")
calls = collections.Counter()
for ln in lines:
    for m in re.finditer(r"(statmodifymanager\.\w+|luamanager\.\w+|checkpointmanager\.\w+)\(", ln):
        calls[m.group(1)] += 1
for k, v in calls.most_common(12):
    print("  %-42s %d" % (k, v))
print("\n=== 选项2 开头 30 行（看效果写法）")
i = [n for n, l in enumerate(lines) if "--index:O_6_6_2_Break_01_001" in l][0]
for k in range(i, i + 26):
    print("  %5d|%s" % (k + 1, lines[k][:110]))
