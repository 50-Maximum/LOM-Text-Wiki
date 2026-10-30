# -*- coding: utf-8 -*-
"""接入人工整理的地图事件名（data/map_event_names.json）：原生 dev > 整理名 > 剧本标题 > 地点＋结果。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

# 1) 载入表
anchor = "_EVT_TITLE = {}"
add = '''MAP_EVT_NAME = {}
try:
    _mn = os.path.join(BASE, "data", "map_event_names.json")
    if os.path.exists(_mn):
        MAP_EVT_NAME = json.load(open(_mn, encoding="utf-8"))
except Exception:
    MAP_EVT_NAME = {}

_EVT_TITLE = {}'''
assert anchor in s and "MAP_EVT_NAME" not in s
s = s.replace(anchor, add, 1)

# 2) 命名优先级
old = '''    title = _t2s((d.get("dev") or "").strip())
    title_src = "原生标题" if title else ""
    if not title:'''
new = '''    title = _t2s((d.get("dev") or "").strip())
    title_src = "原生标题" if title else ""
    if not title and MAP_EVT_NAME.get(nm):
        title = _t2s(MAP_EVT_NAME[nm])
        title_src = "整理命名"
    if not title:'''
assert old in s
s = s.replace(old, new, 1)

open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("整理命名已接入")
