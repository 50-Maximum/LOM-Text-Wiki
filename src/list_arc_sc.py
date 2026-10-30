# -*- coding: utf-8 -*-
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
d = json.load(open(os.path.join(B, "arcs.json"), encoding="utf-8"))
sc = d.get("scene") or {}
print("人工指定场景 %d 条：" % len(sc))
for k, v in sorted(sc.items()):
    print("   %-26s %s" % (k, v))
