# -*- coding: utf-8 -*-
import io, sys, os, glob, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"D:\LegendOfMortal Wiki\data\raw\scripts"
fs = sorted(glob.glob(os.path.join(base, "*.txt")))
pat = re.compile(r'(>=|<=|==|~=)\s*-?\d')
shown = 0
for f in fs:
    t = open(f, encoding="utf-8", errors="replace").read()
    ls = t.splitlines()
    idxs = [i for i, ln in enumerate(ls) if pat.search(ln) and not ln.strip().startswith("--")]
    if idxs and shown < 3:
        print("\n====", os.path.basename(f), "====")
        for i in idxs[:14]:
            print("  %4d| %s" % (i, ls[i].strip()[:170]))
        shown += 1
# GetStat 上下文
print("\n#### GetStat ####")
for f in fs:
    t = open(f, encoding="utf-8", errors="replace").read()
    if "GetStat" in t:
        ls = t.splitlines()
        print("\n--", os.path.basename(f))
        for i, ln in enumerate(ls):
            if "GetStat" in ln:
                print("  %4d| %s" % (i, ln.strip()[:170]))
