# -*- coding: utf-8 -*-
import io, sys, os, glob, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"D:\LegendOfMortal Wiki\data\raw\scripts"
fs = sorted(glob.glob(os.path.join(base, "*.txt")))
want = ("SetCurrentStoryScript", "SetCurrentTravelScript", "SetTempScript", "statmodifymanager.AddStory")
for w in want:
    print("\n########", w)
    n = 0
    for f in fs:
        ls = open(f, encoding="utf-8", errors="replace").read().splitlines()
        for i, ln in enumerate(ls):
            if w in ln:
                print("  --", os.path.basename(f), "第", i, "行")
                for j in range(max(0, i - 3), min(len(ls), i + 3)):
                    print("    %4d| %s" % (j, ls[j].strip()[:150]))
                n += 1
                break
        if n >= 2:
            break
