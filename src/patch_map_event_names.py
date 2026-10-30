# -*- coding: utf-8 -*-
"""地图事件命名：没有 dev 名字的，用「地点・结果文案」补名（结果取自 key）。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

old = '''    title = (d.get("dev") or "").strip()
    title = (place + "・" + title) if (place and title) else (title or nm)'''
new = '''    title = _t2s((d.get("dev") or "").strip())
    if not title:
        _k = _t2s((d.get("key") or "").replace("_", " ").strip())
        if place and _k:
            title = place + "・" + _k
        else:
            title = place or _k or nm
    else:
        title = (place + "・" + title) if place else title'''
assert old in s
s = s.replace(old, new, 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("地图事件命名规则已补")
