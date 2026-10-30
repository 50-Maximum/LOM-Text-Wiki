# -*- coding: utf-8 -*-
"""事件页「触发条件」去重（同一条件被多场重复带入时只留一条）。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

old = '''        if crows:
            secs.insert(0, {"h": "触发条件", "rows": crows[:16]})'''
new = '''        if crows:
            _seen_note, _crow2 = set(), []
            for _r in crows:
                _k = (_r.get("note") or "").strip()
                if _k and _k in _seen_note:
                    continue
                _seen_note.add(_k)
                _crow2.append(_r)
            secs.insert(0, {"h": "触发条件", "rows": _crow2[:16]})'''
assert old in s
s = s.replace(old, new, 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("触发条件已去重")
