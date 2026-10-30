# -*- coding: utf-8 -*-
import io, sys, os, glob, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"D:\LegendOfMortal Wiki\data\raw\scripts"
fs = sorted(glob.glob(os.path.join(base, "*.txt")))
keys = ("checkpointmanager.Position", "SetNextScript", "Mission(", "HasFlag", "GetFlag", "statmodifymanager.Get")
cnt = collections.Counter()
files_with = collections.defaultdict(list)
for f in fs:
    t = open(f, encoding="utf-8", errors="replace").read()
    for k in keys:
        n = t.count(k)
        if n:
            cnt[k] += n
            files_with[k].append((os.path.basename(f), n))
print("总计:", dict(cnt))
for k in keys:
    print("\n== %s == 文件数 %d" % (k, len(files_with[k])))
    for nm, n in sorted(files_with[k], key=lambda x: -x[1])[:8]:
        print("   %-28s %d" % (nm, n))
# 看 Position 上下文
for f in fs:
    t = open(f, encoding="utf-8", errors="replace").read()
    if "checkpointmanager.Position" in t:
        ls = t.splitlines()
        print("\n==== 样例", os.path.basename(f), "====")
        for i, ln in enumerate(ls):
            if "Position" in ln:
                for j in range(max(0, i - 6), min(len(ls), i + 6)):
                    print("  %4d| %s" % (j, ls[j].strip()[:150]))
                break
        break
