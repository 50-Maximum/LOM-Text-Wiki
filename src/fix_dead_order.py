# -*- coding: utf-8 -*-
"""把「删除已合并旧页」的过滤挪到写库前（原位置在 _DEAD 定义之前，顺序错了）。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(S, encoding="utf-8").read()

block = ('if _DEAD:\n    pages = [p for p in _pp if p[0] not in _DEAD]\n'
         '    print("删除已合并的旧页", len(_DEAD), "个")')
if block in s:
    s = s.replace(block + "\n", "", 1)
    print("已移除错位的过滤块")

anchor = 'c.executemany("insert or replace into pages values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", pages)'
assert anchor in s
new = ('if _DEAD:\n'
       '    pages = [p for p in pages if p[0] not in _DEAD]\n'
       '    print("删除已合并的旧页", len(_DEAD), "个")\n\n' + anchor)
if "删除已合并的旧页" not in s.split(anchor)[0]:
    s = s.replace(anchor, new, 1)
    print("已把过滤移到写库前")
open(S, "w", encoding="utf-8").write(s)
print("done")
