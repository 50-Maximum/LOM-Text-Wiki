# -*- coding: utf-8 -*-
import io, sys, os, glob, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"D:\LegendOfMortal Wiki\data\raw\scripts"
fs = sorted(glob.glob(os.path.join(base, "*.txt")))
pat = re.compile(r'ChangeScene\s*\(\s*"([^"]+)"')
n_hits = 0
shown = 0
targets = collections.Counter()
for f in fs:
    t = open(f, encoding="utf-8", errors="replace").read()
    ls = t.splitlines()
    for i, ln in enumerate(ls):
        m = pat.search(ln)
        if m:
            n_hits += 1
            targets[m.group(1)] += 1
            if shown < 2:
                print("\n====", os.path.basename(f), "第", i, "行 ====")
                for j in range(max(0, i - 12), min(len(ls), i + 3)):
                    print("  %4d| %s" % (j, ls[j].strip()[:150]))
                shown += 1
print("\nChangeScene 调用数:", n_hits, " 目标数:", len(targets))
# 关键词：是否 Condition 保护
cond_before = 0
for f in fs:
    ls = open(f, encoding="utf-8", errors="replace").read().splitlines()
    for i, ln in enumerate(ls):
        if pat.search(ln):
            win = "\n".join(ls[max(0, i - 25):i])
            if "checkpointmanager.Condition" in win or "switch" in win.lower() or "choice" in win.lower():
                cond_before += 1
print("位于条件块内的 ChangeScene:", cond_before)

# Condition 旗标清单
flags = collections.Counter()
for f in fs:
    t = open(f, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r'checkpointmanager\.Condition\("([^"]+)"\)', t):
        flags[m.group(1)] += 1
print("\nCondition 旗标种类:", len(flags), " 总次数:", sum(flags.values()))
print("样例:", list(flags.items())[:10])
