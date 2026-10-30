# -*- coding: utf-8 -*-
"""看剧情段数据结构：segments / seg_of / route_of 的形态。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
d = json.load(open(r"D:\LegendOfMortal Wiki\data\story_segments.json", encoding="utf-8"))
print("keys:", list(d.keys()))
seg = d.get("segments") or []
print("segments 数:", len(seg))
if seg:
    s0 = seg[0]
    print("segments[0] 类型:", type(s0).__name__)
    print("segments[0]:", json.dumps(s0, ensure_ascii=False)[:400])
so = d.get("seg_of") or {}
print("seg_of 条数:", len(so))
print("seg_of 样例:", list(so.items())[:5])
