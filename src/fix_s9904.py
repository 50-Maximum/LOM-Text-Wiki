# -*- coding: utf-8 -*-
"""S9904_01 按五零判定归眉山（偏僻小镇即在眉山一带）。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\place_override.json"
ov = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
ov["S9904_01"] = {"place": "眉山",
                  "why": "山贼自陈「绕远路到这偏僻小镇，避开你唐门的地界」，五零判定按眉山计"}
json.dump(ov, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("覆盖表", len(ov), "条；S9904_01 ->", ov["S9904_01"]["place"])
