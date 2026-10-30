# -*- coding: utf-8 -*-
"""看 condition / enable / require 这些关键字在剧本里到底长什么样。"""
import io, sys, os, re, glob, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAW = r"D:\LegendOfMortal Wiki\data\raw\scripts"

samples = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(RAW, "*.txt"))):
    for i, ln in enumerate(open(f, encoding="utf-8", errors="replace")):
        low = ln.lower()
        for k in ("condition", "enable", "require", "unlock"):
            if k in low and len(samples[k]) < 6:
                samples[k].append((os.path.basename(f), ln.strip()[:130]))

for k in ("condition", "enable", "require", "unlock"):
    print("=== " + k)
    for s in samples[k]:
        print("  ", s[0], "|", s[1])
    print()
