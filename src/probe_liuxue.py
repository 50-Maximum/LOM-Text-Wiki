# -*- coding: utf-8 -*-
"""留学选项原文 + 心上人机制。"""
import os, sys, io, re, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "scripts")
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))

print("== meeting_option_01 原始脚本里含 青城/崆峒 的行 ==")
p = os.path.join(RAW, "meeting_option_01.txt")
if os.path.exists(p):
    for i, ln in enumerate(open(p, encoding="utf-8"), 1):
        if "青城" in ln or "崆峒" in ln or "留学" in ln:
            print(f"  {i}: {ln.rstrip()[:120]}")
else:
    print("  文件不存在")

print("\n== 全库脚本里 心上人 出现处 ==")
hits = 0
for fn in sorted(os.listdir(RAW)):
    if not fn.endswith(".txt"):
        continue
    s = open(os.path.join(RAW, fn), encoding="utf-8").read()
    if "心上人" in s:
        hits += 1
        for i, ln in enumerate(s.splitlines(), 1):
            if "心上人" in ln:
                print(f"  {fn}:{i} {ln.strip()[:110]}")
    if hits > 8:
        break

print("\n== flags 表里所有中文名旗标 ==")
for r in c.execute("select distinct flag from flags where flag like '%心%' or flag like '%情%' limit 20"):
    print("  ", r[0])
