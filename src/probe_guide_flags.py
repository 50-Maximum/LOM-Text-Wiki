# -*- coding: utf-8 -*-
import io, sys, os, glob, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
d = r"D:\LegendOfMortal Wiki\data\guide"
fs = sorted(glob.glob(os.path.join(d, "*.txt")))
print("攻略文本:", len(fs))
tot = {"🚩": 0, "触发": 0, "条件": 0, "前置": 0}
for f in fs:
    t = open(f, encoding="utf-8", errors="replace").read()
    c = {k: t.count(k) for k in tot}
    print("  %-28s %6d 字  🚩%3d 触发%4d 条件%3d 前置%3d" % (os.path.basename(f), len(t), c["🚩"], c["触发"], c["条件"], c["前置"]))
    for k in tot:
        tot[k] += c[k]
print("合计:", tot)
# 看一段含 🚩 的上下文
for f in fs:
    t = open(f, encoding="utf-8", errors="replace").read()
    i = t.find("🚩")
    if i > 0:
        print("\n样例（%s）：" % os.path.basename(f))
        print(t[max(0, i - 200): i + 300])
        break
