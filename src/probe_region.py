# -*- coding: utf-8 -*-
"""调试 ch6_6_2_break_start_01 的 index 标记、区域边界、跳转命中。"""
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
f = r"D:\LegendOfMortal Wiki\data\raw\scripts\ch6_6_2_break_start_01.txt"
lines = open(f, encoding="utf-8", errors="replace").read().split("\n")
RE_INDEX = re.compile(r"--index:\s*(O_[A-Za-z0-9_]+)")
RE_BRANCH = re.compile(r"^\s*(?:if|elseif)\s+(\w+)\s*==\s*(\d+)\s+then\s*$")
RE_JUMP = re.compile(r'(?:SetNextScript|ChangeScene)\(\s*"([^"]+)"')

marks = [(i, RE_INDEX.search(l).group(1)) for i, l in enumerate(lines) if RE_INDEX.search(l)]
print("标记 %d 个" % len(marks))
for li, key in marks[:3] + marks[-2:]:
    print("  行%d %s" % (li + 1, key))

li, key = [m for m in marks if m[1].endswith("014")][0]
print("\n目标标记行", li + 1, key)
for k in range(max(0, li - 6), li + 1):
    print("  %5d|%s" % (k + 1, lines[k][:100]))
print("\n后续 40 行（含缩进）:")
for k in range(li, min(li + 40, len(lines))):
    print("  %5d|%s" % (k + 1, lines[k][:100].replace("\t", "→")))
