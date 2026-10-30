# -*- coding: utf-8 -*-
"""查文本总表里有没有地图事件的显示名表：看键前缀与含「失敗」的键。"""
import io, json, os, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
T = json.load(open(r"D:\LegendOfMortal Wiki\data\build\text.json", encoding="utf-8"))
print("键总数", len(T))
pref = collections.Counter(k.split("_")[0] for k in T)
print("前缀 top20:", pref.most_common(20))

cand = [k for k in T if any(w in k for w in ("失敗", "失败", "PositionEvent", "PosEvent", "MapEvent", "EventName", "大成功"))]
print("\n疑似结果/事件名键:", len(cand))
for k in cand[:15]:
    print("   ", k, "=", str(T[k])[:40])

# 文本表里有没有值就是这些代码名
rev = {v: k for k, v in T.items()}
for nm in ["Alchemy_Work_BF_01", "Door_02_E_01"]:
    print("\n值命中", nm, "→", rev.get(nm))
