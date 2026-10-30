# -*- coding: utf-8 -*-
"""看地图事件的原始记录里有哪些字段，能不能推出中文名。"""
import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\data\position_events.json"
d = json.load(open(P, encoding="utf-8"))
print("条数:", len(d))

def show(k):
    v = d.get(k)
    print("\n==", k)
    print(json.dumps(v, ensure_ascii=False)[:800])

for k in ["Alchemy_Work_BF_01", "Back_02_N_01", "Alchemy_Work_E_01"]:
    show(k)

# 字段名统计
keys = set()
for v in list(d.values())[:50]:
    if isinstance(v, dict):
        keys.update(v)
print("\n字段:", sorted(keys))
