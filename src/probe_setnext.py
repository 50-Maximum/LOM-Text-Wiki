# -*- coding: utf-8 -*-
import io, sys, os, re, glob, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"D:\LegendOfMortal Wiki\data\raw\scripts"
fs = sorted(glob.glob(os.path.join(base, "*.txt")))
pSet = re.compile(r'SetNextScript\(\s*"([^"]+)"')
pIf = re.compile(r'^\s*(if|elseif)\s+(.+?)\s+then\s*$')
stats = collections.Counter()
examples = []
for f in fs:
    ls = open(f, encoding="utf-8", errors="replace").read().splitlines()
    depth = 0
    stack = []
    for i, ln in enumerate(ls):
        s = ln.strip()
        m = pIf.match(s)
        if m:
            stack.append(m.group(2))
        if s.startswith("end"):
            if stack:
                stack.pop()
        m2 = pSet.search(s)
        if m2:
            stats["total"] += 1
            if stack:
                stats["在 if 内"] += 1
                if len(examples) < 10:
                    examples.append((os.path.basename(f), m2.group(1), stack[-1][:80]))
print(dict(stats))
for e in examples:
    print("   %-28s -> %-18s 条件: %s" % e)
# 统计 if 条件里出现 switch/condition 变量的比例
cnt = collections.Counter()
for f in fs:
    t = open(f, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r'if\s+(\w+)\s*==\s*(\d+)\s+then', t):
        cnt[m.group(1).split("_")[0]] += 1
print("\nif 变量前缀:", cnt.most_common(8))
