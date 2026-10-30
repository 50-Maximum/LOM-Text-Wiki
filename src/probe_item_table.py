# -*- coding: utf-8 -*-
"""看 Lua 里物品表的字段结构（含 Misc/Name 引用的上下文）。"""
import io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAW = r"D:\LegendOfMortal Wiki\data\raw"
hits = 0
for dirpath, _, fs in os.walk(RAW):
    for f in fs:
        if not f.endswith(".txt"):
            continue
        p = os.path.join(dirpath, f)
        s = open(p, encoding="utf-8", errors="ignore").read()
        if "Misc/Name/" in s or "Special/Name/" in s:
            i = s.find("Misc/Name/")
            if i < 0:
                i = s.find("Special/Name/")
            print("==", os.path.relpath(p, RAW))
            print(s[max(0, i - 400):i + 400])
            hits += 1
            if hits >= 2:
                sys.exit()
print("命中文件", hits)
