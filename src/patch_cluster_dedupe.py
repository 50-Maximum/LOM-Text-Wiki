# -*- coding: utf-8 -*-
"""去重：同一场景上来自不同上游、内容相同的嵌套分支组只显示一次。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

old = '''        _rows_c = []
        for _k, _m in enumerate(_mem):'''
new = '''        _rows_c = []
        _sig_seen = set()
        for _k, _m in enumerate(_mem):'''
assert old in s
s = s.replace(old, new, 1)

old2 = '''            _c = CLUSTER_BY_ID.get(_m.get("cluster")) or {}
            if not _c:
                continue'''
new2 = '''            _c = CLUSTER_BY_ID.get(_m.get("cluster")) or {}
            if not _c:
                continue
            _sig = (_c.get("switch") or "", _m.get("alt"), tuple(_m.get("results") or []),
                    len(_c.get("alts") or []),
                    tuple(sorted("/".join(a.get("results") or []) + "|" + str(len(a.get("scenes") or []))
                                 for a in (_c.get("alts") or []))))
            if _sig in _sig_seen:
                continue
            _sig_seen.add(_sig)'''
assert old2 in s
s = s.replace(old2, new2, 1)

open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("嵌套分支组去重已接入")
