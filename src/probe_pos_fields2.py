# -*- coding: utf-8 -*-
"""position_events.json 是列表，看单条结构与能否推出中文名。"""
import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\data\position_events.json"
d = json.load(open(P, encoding="utf-8"))
print("条数:", len(d), "类型:", type(d[0]).__name__)
print("\n第一条:", json.dumps(d[0], ensure_ascii=False)[:600])

keys = set()
for v in d[:80]:
    if isinstance(v, dict):
        keys.update(v)
print("\n字段:", sorted(keys))

for k in ["Alchemy_Work_BF_01", "Back_02_N_01"]:
    for v in d:
        if isinstance(v, dict) and (v.get("key") == k or v.get("dev") == k or v.get("id") == k):
            print("\n==", k, json.dumps(v, ensure_ascii=False)[:500])
            break
