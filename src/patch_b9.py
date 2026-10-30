# -*- coding: utf-8 -*-
"""两件事：
① 改名合并后旧页直接删掉（不再留隐藏页，只保留重定向）；
② 地点页补「发生场景」栏（按场景 attribution 反查，最多 60 条）。
"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(S, encoding="utf-8").read()

# ① 旧页删除
old = """    pages[_idx[_so]] = (_po[0], _po[1], _po[2], _po[3], _po[4], _po[5], _po[6],
                        _po[7], _po[8], _po[9], _po[10], 1, _po[12], _po[13])
    redirects.append((_so, _sn))"""
new = """    _DEAD.add(_so)
    redirects.append((_so, _sn))"""
if old in s:
    s = s.replace(old, new, 1)
    print("改名合并：改为删除旧页")
elif "_DEAD.add(_so)" in s:
    print("已是删除模式")
else:
    print("!! 未找到隐藏旧页的代码")

# 删除集合声明 + 过滤
if "_DEAD = set()" not in s:
    anchor = "# 改名后残留的旧页面：内容并入新页面，旧页删除并加重定向"
    assert anchor in s
    s = s.replace(anchor, anchor + "\n_DEAD = set()", 1)

if '_DEAD = set()' in s and "if _p[0] not in _DEAD" not in s:
    anchor2 = 'pages = _pp'
    assert anchor2 in s
    s = s.replace(anchor2, anchor2 + '\nif _DEAD:\n    pages = [p for p in _pp if p[0] not in _DEAD]\n'
                  '    print("删除已合并的旧页", len(_DEAD), "个")', 1)
    print("已加旧页过滤")

# ② 地点页「发生场景」
if "SCENES_BY_PLACE" not in s:
    anchor3 = 'CH_ORDER = {"序章": 0, "第0章": 1, "第1章": 2}'
    assert anchor3 in s
    add3 = anchor3 + '''

# 地点 → 场景（按 place_of 反查，供地点页「发生场景」栏）
SCENES_BY_PLACE = {}
try:
    for _s7 in scenes:
        _p7, _e7 = place_of(_s7)
        if _p7:
            SCENES_BY_PLACE.setdefault(_p7, []).append(_s7)
except Exception:
    SCENES_BY_PLACE = {}
'''
    s = s.replace(anchor3, add3, 1)
    print("已建 SCENES_BY_PLACE")

if '_SC_AT' not in s:
    anchor4 = '        _root = name\n        _seen_r = set()'
    assert anchor4 in s
    add4 = '''        _SC_AT = sorted(SCENES_BY_PLACE.get(name, []), key=lambda x: ORDER.get(x, 99999))
        if _SC_AT:
            secs.append({"h": "发生场景", "rows": [
                {"note": scenes.get(_x, {}).get("title") or _x, "quote": "",
                 "script": _x, "title": scenes.get(_x, {}).get("title") or _x,
                 "seq": 0, "routes": []} for _x in _SC_AT[:60]]})
        _root = name
        _seen_r = set()'''
    s = s.replace(anchor4, add4, 1)
    print("已加地点页发生场景栏")

open(S, "w", encoding="utf-8").write(s)
print("patch 完成")
