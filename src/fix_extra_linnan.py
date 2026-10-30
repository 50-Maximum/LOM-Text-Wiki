# -*- coding: utf-8 -*-
import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\extra_persons.json"
d = json.load(open(p, encoding="utf-8"))
n = 0
for k, v in d.items():
    f = (v or {}).get("faction")
    if f == "岭南派":
        v["faction"] = "岭南剑派"
        n += 1
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("补充人物势力改判", n, "条")
