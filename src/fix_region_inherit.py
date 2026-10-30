# -*- coding: utf-8 -*-
"""区域判定改为沿上级链回溯：子女继承父级区域（千金方医馆→江陵→荆湖、都江客栈→青城山→川蜀）。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()
old = '''def _region_of(nm):
    n = nm or ""
    if n in REGION_MAP:
        return REGION_MAP[n]
    for pre, reg in PREFIX_REGION:
        if n.startswith(pre):
            return reg
    return "其他"'''
new = '''def _region_of(nm):
    """自身没登记就沿上级链回溯；都江客栈→青城山镇→青城山→川蜀。"""
    n = nm or ""
    seen = set()
    while n and n not in seen:
        seen.add(n)
        if n in REGION_MAP:
            return REGION_MAP[n]
        for pre, reg in PREFIX_REGION:
            if n.startswith(pre):
                return reg
        n = PPARENT.get(n) or ""
    return "其他"'''
assert old in s
open(P, "w", encoding="utf-8").write(s.replace(old, new))
print("区域判定：支持沿上级链回溯")
