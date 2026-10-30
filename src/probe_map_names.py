# -*- coding: utf-8 -*-
"""找地图事件代码名在游戏文本里的对应条目（有没有中文名）。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAW = r"D:\LegendOfMortal Wiki\data\raw"
keys = ["Alchemy_Work_BF_01", "Back_02_N_01", "Alchemy_Work_F_01"]
hits = {k: [] for k in keys}
for root, ds, fs in os.walk(RAW):
    for f in fs:
        p = os.path.join(root, f)
        try:
            t = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        for k in keys:
            if k in t:
                i = t.find(k)
                hits[k].append((os.path.relpath(p, RAW), t[max(0, i - 60):i + 90].replace("\n", " ")))
for k, v in hits.items():
    print("\n==", k, "命中", len(v))
    for p, ctx in v[:3]:
        print("   ", p, "|", ctx[:150])
