# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"D:\LegendOfMortal Wiki\data\raw\scripts"
for name in ("S0208_01.txt", "door_free_501.txt", "section_01_free_08.txt"):
    p = os.path.join(base, name)
    if not os.path.exists(p):
        print("缺:", name); continue
    t = open(p, encoding="utf-8", errors="replace").read()
    print("\n======", name, "共", len(t), "字节 ======")
    for i, ln in enumerate(t.splitlines()[:45]):
        print("  %3d| %s" % (i, ln.strip()[:140]))
