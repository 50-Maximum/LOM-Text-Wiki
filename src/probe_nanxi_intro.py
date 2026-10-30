# -*- coding: utf-8 -*-
"""在 intros_*.json 里找南溪，并看脚注结构。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
for fn in ("intros_char.json", "intros_world.json", "factions_fix.json", "intros_place.json"):
    p = r"D:\LegendOfMortal Wiki\data\\" + fn
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception as e:
        print(fn, "读取失败", e)
        continue
    hits = [k for k in d if "南溪" in str(k)]
    print(fn, "条目", len(d), "命中", hits[:5])
    for k in hits[:1]:
        print(json.dumps({k: d[k]}, ensure_ascii=False, indent=1)[:1200])
