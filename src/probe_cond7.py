# -*- coding: utf-8 -*-
import io, sys, os, glob, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"D:\LegendOfMortal Wiki\data\raw\scripts"
fs = sorted(glob.glob(os.path.join(base, "*.txt")))
p = re.compile(r'ChangeScene\s*\(\s*"([^"]+)"')
c = collections.Counter()
for f in fs:
    for m in p.finditer(open(f, encoding="utf-8", errors="replace").read()):
        c[m.group(1)] += 1
print("ChangeScene 目标:", c.most_common(20))
print("\n文件名含 free/Free:", [os.path.basename(x) for x in fs if "free" in os.path.basename(x).lower()])
# 找 Free 场景逻辑所在：搜索 "Free" 作为场景名定义
for f in fs:
    t = open(f, encoding="utf-8", errors="replace").read()
    if re.search(r'(SceneName|scene\s*=|scenename)', t[:2000], re.I) and "Free" in t[:3000]:
        print("候选:", os.path.basename(f), len(t))
