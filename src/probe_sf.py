# -*- coding: utf-8 -*-
"""看 scene_flags.json 里 requires/sets 的真实写法。"""
import json, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
d = json.load(open(r"D:\LegendOfMortal Wiki\data\scene_flags.json", encoding="utf-8"))

shown = 0
for s, info in d.items():
    if info.get("requires") and shown < 12:
        print(f"\n{s}  requires:")
        for r in info["requires"][:6]:
            print("   ", repr(r))
        shown += 1

print("\n== sets 样本 ==")
n = 0
for s, info in d.items():
    if info.get("sets") and n < 8:
        print("  ", s, info["sets"])
        n += 1

print("\n== 统计 ==")
print("有 requires", sum(1 for x in d.values() if x.get("requires")))
print("有 sets", sum(1 for x in d.values() if x.get("sets")))
