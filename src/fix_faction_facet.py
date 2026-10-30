# -*- coding: utf-8 -*-
"""势力筛选改成类型（门派/帮派/教门/世家/联盟组织/其他），去掉「顶层」。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

helper = '''

def _faction_type(nm):
    n = nm or ""
    if n.endswith("世家"):
        return "世家"
    if n.endswith("帮"):
        return "帮派"
    if n.endswith("教"):
        return "教门"
    if n.endswith(("派", "门", "剑阁", "阁", "楼", "宫", "寺", "观")):
        return "门派"
    if n.endswith(("盟", "会", "寨", "堡", "堂")):
        return "联盟组织"
    return "其他"


# 缺页的上级地点'''
if "_faction_type" not in s:
    s = s.replace("\n\n# 缺页的上级地点", helper, 1)

marker = '        if _typ == "地点":'
assert marker in s
if '_typ == "势力" and "势力类型"' not in s:
    s = s.replace(marker, '''        if _typ == "势力":
            _f1 = _faction_type(_nm)
        if _typ == "地点":''', 1)

open(P, "w", encoding="utf-8").write(s)
print("build_wiki2 已加势力类型筛选")
