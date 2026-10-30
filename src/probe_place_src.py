# -*- coding: utf-8 -*-
"""找场景里表示「地点」的原始调用：背景 / 场景加载 / Place 表。"""
import io, sys, os, re, glob, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(B, "data", "raw")
f = os.path.join(RAW, "scripts", "ch6_7_1.txt")
s = open(f, encoding="utf-8", errors="replace").read()
print("=== ch6_7_1 里带 back/scene/place/stage.Load 的行")
for ln in s.split("\n"):
    if re.search(r"(background|Background|LoadScene|SetScene|scene\.|stage\.load|场景|Place)", ln):
        print("  ", ln.strip()[:130])

print("\n=== raw 目录结构")
for d in sorted(os.listdir(RAW))[:20]:
    p = os.path.join(RAW, d)
    if os.path.isdir(p):
        n = len(glob.glob(os.path.join(p, "*")))
        print("  %-18s %d 个文件" % (d, n))

print("\n=== system 里含 Place/Scene 的表")
for fn in sorted(glob.glob(os.path.join(RAW, "system", "*"))):
    b = os.path.basename(fn)
    if re.search(r"(Place|Scene|Map|Location)", b, re.I):
        print("  ", b)
        head = open(fn, encoding="utf-8", errors="replace").read().split("\n")[:5]
        for x in head:
            print("      ", x[:120])
