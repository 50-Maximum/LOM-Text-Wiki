# -*- coding: utf-8 -*-
"""地图事件命名升级为三层：原生 dev 标题 > 对应剧本的场景标题 > 地点・结果。"""
import io, re, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

old = '''    title = _t2s((d.get("dev") or "").strip())
    if not title:
        _k = _t2s((d.get("key") or "").replace("_", " ").strip())
        if place and _k:
            title = place + "・" + _k
        else:
            title = place or _k or nm
    else:
        title = (place + "・" + title) if place else title'''
new = '''    title = _t2s((d.get("dev") or "").strip())
    title_src = "原生标题" if title else ""
    if not title:
        _st = _EVT_TITLE.get(nm) or ""
        if _st and len(_st) >= 4 and not re.search(r"（\\d+）$|・工作$|・自由行动$|^转场", _st):
            title = _st
            title_src = "取自剧本标题"
    if not title:
        _k = _t2s((d.get("key") or "").replace("_", " ").strip())
        if place and _k:
            title = place + "・" + _k
        else:
            title = place or _k or nm
        title_src = "地点＋结果"
    else:
        title = (place + "・" + title) if (place and title_src == "原生标题") else title'''
assert old in s
s = s.replace(old, new, 1)

# inf 里记录命名来源
old2 = '''    inf = {"类型": "地图事件", "事件编号": nm}'''
new2 = '''    inf = {"类型": "地图事件", "事件编号": nm}
    if title_src and title_src != "原生标题":
        inf["名称来源"] = title_src'''
assert old2 in s
s = s.replace(old2, new2, 1)

# 预载 事件名→剧本标题
if "_EVT_TITLE" not in s.split("_pe_seen = {}")[0]:
    anchor = '''_pe_seen = {}
for d in POSEV:'''
    add = '''_EVT_TITLE = {}
for _nm, _sc in (_pem or {}).items():
    if not isinstance(_sc, str):
        continue
    try:
        _r = c.execute("select title from scenes where script=?", (_sc,)).fetchone()
    except Exception:
        _r = None
    if _r and _r[0]:
        _EVT_TITLE[_nm] = _t2s(_r[0])

_pe_seen = {}
for d in POSEV:'''
    assert anchor in s
    s = s.replace(anchor, add, 1)

open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("三层命名已接入")
