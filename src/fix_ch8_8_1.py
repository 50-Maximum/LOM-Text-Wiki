# -*- coding: utf-8 -*-
"""ch8_8_1 改判唐门（小竹的愿望 / 武林盟进攻唐门）。"""
import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\data\place_manual.json"
m = json.load(open(P, encoding="utf-8"))
m["ch8_8_1"] = {"place": "唐门", "src": "人工指定"}
json.dump(m, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("place_manual:", len(m), "条；ch8_8_1 → 唐门")
