# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
nxt = json.load(open(B + r"\scene_next.json", encoding="utf-8"))
T = "ch5_4_8_9"
print("=== 指向", T, "的剧本")
for s, d in nxt.items():
    if (d.get("next") == T):
        print("   [无条件] %s" % s)
    for e in (d.get("edges") or []):
        if e.get("target") == T:
            print("   [条件] %-22s %s" % (s, e.get("cond")))
print("\n=== 该剧本自身出口")
d = nxt.get(T) or {}
print("   next:", d.get("next"), " edges:", [(e.get("target"), e.get("cond")) for e in (d.get("edges") or [])])
