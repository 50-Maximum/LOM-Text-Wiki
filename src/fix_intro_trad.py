# -*- coding: utf-8 -*-
"""简介文件里的引文/正文一起转简中（lines 已转，旧脚注里的繁体引文因此对不上）。"""
import io, sys, json
from opencc import OpenCC
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
CC = OpenCC("t2s")
B = r"D:\LegendOfMortal Wiki\data"

def walk(o):
    if isinstance(o, str):
        return CC.convert(o)
    if isinstance(o, list):
        return [walk(x) for x in o]
    if isinstance(o, dict):
        return {k: walk(v) for k, v in o.items()}
    return o

for fn in ("intros_char.json", "intros_world.json", "factions_fix.json"):
    p = B + "\\" + fn
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception as e:
        print(fn, "跳过", e); continue
    before = json.dumps(d, ensure_ascii=False)
    d2 = walk(d)
    after = json.dumps(d2, ensure_ascii=False)
    if before != after:
        json.dump(d2, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        diff = sum(1 for a, b in zip(before, after) if a != b)
        print("%-20s 已转简（字符差异约 %d）" % (fn, diff))
    else:
        print("%-20s 无需改动" % fn)
