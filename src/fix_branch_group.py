# -*- coding: utf-8 -*-
"""分支点按目标合并结果号，便于阅读。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_scene_graph.py"
s = open(P, encoding="utf-8").read()

old = '''        tgt = []
        _seen = set()
        for e in sorted(es, key=lambda x: (len(x["cond"] or ""), x["line"])):
            _k = (e["result"], e["to"])
            if _k in _seen:
                continue
            _seen.add(_k)
            if any(x["result"] == e["result"] for x in tgt):
                continue
            tgt.append({"result": e["result"], "to": e["to"], "type": e["type"]})'''
new = '''        tgt, _by = [], {}
        for e in sorted(es, key=lambda x: (int(x["result"] or 0), len(x["cond"] or ""))):
            d = _by.get(e["to"])
            if d is None:
                d = {"results": [], "to": e["to"], "type": e["type"]}
                _by[e["to"]] = d
                tgt.append(d)
            if e["result"] not in d["results"]:
                d["results"].append(e["result"])'''
assert old in s
s = s.replace(old, new, 1)

old2 = '''        for t in b["targets"]:
            print("     结果%s → %s（%s）%s" % (t["result"], t["to"], t["type"],
                                            nodes.get(t["to"], {}).get("title", "")))'''
new2 = '''        for t in b["targets"]:
            print("     结果%s → %s（%s）%s" % ("/".join(t["results"]), t["to"], t["type"],
                                            nodes.get(t["to"], {}).get("title", "")))'''
assert old2 in s
s = s.replace(old2, new2, 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("分支点改为按目标合组")
