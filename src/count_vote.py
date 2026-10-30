# -*- coding: utf-8 -*-
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
d = json.load(open(os.path.join(B, "research", "arc_by_vote.json"), encoding="utf-8"))
tot = sum(len(v) for v in d.values())
print("投票定阶段合计:", tot)
for k, v in d.items():
    print("  %-12s %d" % (k, len(v)))
