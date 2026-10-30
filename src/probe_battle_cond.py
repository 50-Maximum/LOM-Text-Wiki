# -*- coding: utf-8 -*-
"""看判定库里战斗结果开关的含义（Combat_Result / Battle_Result）。"""
import io, json, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
lib = json.load(open(r"D:\LegendOfMortal Wiki\data\cond_lib.json", encoding="utf-8"))
keys = [k for k in lib if k.startswith(("Combat_Result", "Battle_Result"))]
print("条数", len(keys))
for k in sorted(keys)[:12]:
    print("\n==", k, json.dumps(lib[k], ensure_ascii=False)[:400])
