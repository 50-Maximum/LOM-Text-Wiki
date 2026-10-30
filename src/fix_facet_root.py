# -*- coding: utf-8 -*-
"""保留三级结构，但筛选档只取顶级区域：青城山镇不再单独成档，归入青城山。

规则：
  有上级 → 取最顶层的祖先（青城山/川蜀/岳阳/江陵/崆峒山）
  没上级但有子级 → 自成区域（青城山、岳阳、江陵…）
  没上级也没子级 → 其他
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

old = '''        _facet_pl = PPARENT.get(name) or "其他"'''
new = '''        _has_kids = any(v == name for v in PPARENT.values())
        _facet_pl = (_root if PPARENT.get(name)
                     else (name if _has_kids else "其他"))'''
assert old in s, "未找到 facet 行"
s = s.replace(old, new)
open(P, "w", encoding="utf-8").write(s)
print("facet 规则已改：只保留顶级区域")
