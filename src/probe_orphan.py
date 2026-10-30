# -*- coding: utf-8 -*-
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"D:\LegendOfMortal Wiki\data\raw\scripts"
targets = ["S0012_01_01", "S0017_01", "S0019_01", "S0020_01"]
files = {os.path.splitext(os.path.basename(p))[0]: p for p in glob.glob(os.path.join(base, "*.txt"))}
for t in targets:
    print("\n######## 目标", t, " 自身存在:", t in files)
    n = 0
    for sc, p in files.items():
        ls = open(p, encoding="utf-8", errors="replace").read().splitlines()
        for i, ln in enumerate(ls):
            if '"%s"' % t in ln:
                print("   来自", sc, "第", i, "行:", ln.strip()[:110])
                for j in range(max(0, i - 4), i):
                    print("        %4d| %s" % (j, ls[j].strip()[:110]))
                n += 1
                break
        if n >= 3:
            break
    if not n:
        print("   没有任何脚本引用它（可能是日程/位置事件触发）")
