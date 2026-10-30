# -*- coding: utf-8 -*-
"""成吉思汗归大蒙古国（势力表里本来就有这个势力）。"""
import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\chars_prefix.json"
cp = json.load(open(p, encoding="utf-8"))
print("原：", cp.get("成吉思汗"))
cp["成吉思汗"] = "大蒙古国"
json.dump(cp, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("改为大蒙古国")
