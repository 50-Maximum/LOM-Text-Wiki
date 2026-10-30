# -*- coding: utf-8 -*-
"""修分支点归组：丢掉自环边，同一结果只保留最先出现的一条。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_scene_graph2.py"
s = open(P, encoding="utf-8").read()

old = '''    bp = collections.defaultdict(list)
    for e in edges:
        if e["switch"] and e["result"]:
            bp[(e["from"], e["switch"], e["site"])].append(e)'''
new = '''    bp = collections.defaultdict(list)
    _used = set()
    for e in sorted(edges, key=lambda x: x["line"]):
        if not (e["switch"] and e["result"]):
            continue
        if e["to"] == e["from"]:
            continue
        _k = (e["from"], e["switch"], e["site"], e["result"])
        if _k in _used:
            continue
        _used.add(_k)
        bp[(e["from"], e["switch"], e["site"])].append(e)'''
assert old in s
s = s.replace(old, new, 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("分支点归组已修")
