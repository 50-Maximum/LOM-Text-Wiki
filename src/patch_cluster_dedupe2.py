# -*- coding: utf-8 -*-
"""同型嵌套分支合并：同一场景上「同一判定 + 同一路」的多个上游分支点，只显示一次并注明数量。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

old = '''            _sig = (_c.get("switch") or "", _m.get("alt"), tuple(_m.get("results") or []),
                    len(_c.get("alts") or []),
                    tuple(sorted("/".join(a.get("results") or []) + "|" + str(len(a.get("scenes") or []))
                                 for a in (_c.get("alts") or []))))'''
new = '''            _sig = (_c.get("switch") or "", _m.get("alt"), len(_c.get("alts") or []))'''
assert old in s
s = s.replace(old, new, 1)

# 统计同型数量，并在表头注明
old2 = '''            if _sig in _sig_seen:
                continue
            _sig_seen.add(_sig)'''
new2 = '''            if _sig in _sig_seen:
                _sig_seen[("n",) + _sig] = _sig_seen.get(("n",) + _sig, 1) + 1
                continue
            _sig_seen.add(_sig)'''
assert old2 in s
s = s.replace(old2, new2, 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("同型分支合并已接入")
