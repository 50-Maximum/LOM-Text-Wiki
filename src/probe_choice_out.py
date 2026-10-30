# -*- coding: utf-8 -*-
"""看 P1 产出的 choices 里，S0003_01_02 的选项文案是什么；并看 branch_tree 怎么取文案。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BUILD = r"D:\LegendOfMortal Wiki\data\build"
for fn in sorted(os.listdir(BUILD)):
    print(fn, os.path.getsize(os.path.join(BUILD, fn)))
print()
for fn in os.listdir(BUILD):
    if "choice" in fn.lower():
        p = os.path.join(BUILD, fn)
        for line in open(p, encoding="utf-8"):
            d = json.loads(line)
            if d.get("script") == "S0003_01_02":
                print(fn, json.dumps(d, ensure_ascii=False)[:600])
