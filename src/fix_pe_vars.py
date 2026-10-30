# -*- coding: utf-8 -*-
"""补 PE_TYPE / PE_INTRO 变量定义（上次因函数体里已含该词，守卫判定失效没插入）。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(S, encoding="utf-8").read()
anchor = 'PE_RENAME = PE.get("region_rename") or {}'
assert anchor in s, "PE_RENAME 行未找到"
need = []
if 'PE_TYPE = PE.get("type")' not in s:
    need.append('PE_TYPE = PE.get("type") or {}')
if 'PE_INTRO = PE.get("intro")' not in s:
    need.append('PE_INTRO = PE.get("intro") or {}')
if need:
    s = s.replace(anchor, anchor + "\n" + "\n".join(need), 1)
    open(S, "w", encoding="utf-8").write(s)
    print("已补：", "；".join(need))
else:
    print("变量已存在")
