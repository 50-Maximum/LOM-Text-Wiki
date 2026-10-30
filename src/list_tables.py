# -*- coding: utf-8 -*-
"""列出各 build_*.py 里建的表，用于确定重建顺序。"""
import io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
SRC = r"D:\LegendOfMortal Wiki\src"
for fn in sorted(os.listdir(SRC)):
    if not fn.endswith(".py"):
        continue
    t = open(os.path.join(SRC, fn), encoding="utf-8", errors="ignore").read()
    tabs = re.findall(r"CREATE TABLE(?: IF NOT EXISTS)?\s+(\w+)", t, re.I)
    if tabs:
        print("%-26s %s" % (fn, ", ".join(sorted(set(tabs)))))
