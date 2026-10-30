# -*- coding: utf-8 -*-
"""读关键分支场景的控制流：SetFlag / if / ChangeScene。"""
import os, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
SD = r"D:\LegendOfMortal Wiki\data\raw\scripts"

def show(fn, keys=("SetFlag", "if ", "elseif", "ChangeScene", "choose("), ctx=1):
    p = os.path.join(SD, fn + ".txt")
    if not os.path.exists(p):
        print("缺", fn); return
    lines = open(p, encoding="utf-8").read().splitlines()
    print(f"\n===== {fn}（{len(lines)} 行）=====")
    hit = [i for i, l in enumerate(lines)
           if any(k in l for k in keys) or re.search(r'SetFlag|ChangeScene', l)]
    shown = set()
    for i in hit[:40]:
        for j in range(max(0, i - ctx), min(len(lines), i + ctx + 1)):
            if j in shown: continue
            shown.add(j)
            mark = ">>" if j == i else "  "
            print(f" {mark} {lines[j].rstrip()[:130]}")

for fn in ("ch5_6_8_3", "ch5_6_8_3_4", "ch5_6_8_3_5", "ch5_6_8_3_6"):
    show(fn, ctx=2)
