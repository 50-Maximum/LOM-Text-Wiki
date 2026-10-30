# -*- coding: utf-8 -*-
import io, sys, os, glob, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"D:\LegendOfMortal Wiki\data\raw\scripts"
fs = sorted(glob.glob(os.path.join(base, "*.txt")))
apis = collections.Counter()
for f in fs:
    t = open(f, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r"([A-Za-z_][A-Za-z0-9_]*)\s*\.\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(", t):
        apis[m.group(1) + "." + m.group(2)] += 1
for k, v in apis.most_common(40):
    print("  %-44s %d" % (k, v))
print("\n含 Story/Script/Scene/Mission/Position 的 API:")
for k, v in apis.items():
    if re.search(r"Story|Script|Scene|Mission|Position", k):
        print("  %-44s %d" % (k, v))
