# -*- coding: utf-8 -*-
import io, sys, os, glob, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"D:\LegendOfMortal Wiki\data\raw\scripts"
for p in sorted(glob.glob(os.path.join(base, "*.txt"))):
    t = open(p, encoding="utf-8", errors="replace").read()
    if "checkpointmanager.Dice" not in t:
        continue
    ls = t.splitlines()
    print("====", os.path.basename(p), "====")
    for i, ln in enumerate(ls[:90]):
        s = ln.strip()
        if any(k in s for k in ("Switch", "Dice", "SetRandom", "dicemenudialog", "if ", "result")):
            print("  %3d| %s" % (i, s[:130]))
    break
