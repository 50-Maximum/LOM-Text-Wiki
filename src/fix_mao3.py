# -*- coding: utf-8 -*-
"""毛二壮 彻底并入王二壮：merge + delete + 别名重定向。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
p = os.path.join(B, "chars_fix.json")
d = json.load(open(p, encoding="utf-8"))
d.setdefault("merge", {})["毛二壮"] = "王二壮"
dl = d.setdefault("delete", [])
if "毛二壮" not in dl:
    dl.append("毛二壮")
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("merge=王二壮, delete 已加 毛二壮；delete 现有", len(dl), "条")
