# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ref = json.load(open(r"D:\LegendOfMortal Wiki\data\scene_time_ref.json", encoding="utf-8"))
for sc in ("ch1_1", "ch1_1_break_option", "alchemy_001", "S8400_01",
           "S8300_01", "S9904_01", "S8400_02"):
    v = ref.get(sc) or {}
    print("%-20s %s年%s月%s ｜ %-30s score=%s src=%s"
          % (sc, v.get("year"), v.get("month"), v.get("xun"),
             v.get("name"), v.get("score"), v.get("src", "-")))
print("\n总计 %d 条" % len(ref))
from collections import Counter
print(Counter((v.get("year"), v.get("month"), v.get("xun")) for v in ref.values()).most_common(8))
