# -*- coding: utf-8 -*-
import io, sys, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"D:\LegendOfMortal Wiki\data\raw\scripts"
fs = sorted(glob.glob(os.path.join(base, "*.txt")))
print("文件:", len(fs))
keys = ("checkpointmanager", "Condition", "Dice", "Switch", "SetFlag", "ChangeScene", "GetFlag", "GetStat")
hits = {k: 0 for k in keys}
shown = 0
for f in fs:
    t = open(f, encoding="utf-8", errors="replace").read()
    for k in keys:
        if k in t:
            hits[k] += 1
    if shown < 2 and "checkpointmanager.Condition" in t:
        print("\n====", os.path.basename(f), "====")
        for i, ln in enumerate(t.splitlines()):
            if any(k in ln for k in keys):
                print("  %4d| %s" % (i, ln.strip()[:170]))
        shown += 1
print("\n含各关键字文件数:", hits)
