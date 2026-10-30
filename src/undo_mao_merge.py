# -*- coding: utf-8 -*-
"""撤回 毛二壮→王二壮 并义：毛二壮是丐帮前任帮主，另有笔记 2 条，不是同一人。"""
import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\chars_fix.json"
d = json.load(open(p, encoding="utf-8"))
mg = d.get("merge") or {}
if "毛二壮" in mg:
    print("撤回并义 毛二壮 →", mg.pop("毛二壮"))
else:
    print("merge 里没有 毛二壮")
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("merge 条数", len(mg))
