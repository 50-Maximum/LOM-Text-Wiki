# -*- coding: utf-8 -*-
"""修分支解析：取最内层条件的判定变量；同一结果去重。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_scene_graph.py"
s = open(P, encoding="utf-8").read()

old = '''        sw_id, sw_res = "", ""
        for var, res in RE_SW.findall(cond):
            if var in ck and ck[var][0] == "Switch":
                sw_id, sw_res = ck[var][1], res
                break'''
new = '''        sw_id, sw_res = "", ""
        for _entry in reversed(stack):
            for var, res in RE_SW.findall(_entry or ""):
                if var in ck and ck[var][0] == "Switch":
                    sw_id, sw_res = ck[var][1], res
                    break
            if sw_id:
                break'''
assert old in s
s = s.replace(old, new, 1)

old2 = '''        tgt = []
        for e in es:
            if e["to"] not in [x["to"] for x in tgt]:
                tgt.append({"result": e["result"], "to": e["to"], "type": e["type"]})'''
new2 = '''        tgt = []
        _seen = set()
        for e in sorted(es, key=lambda x: (len(x["cond"] or ""), x["line"])):
            _k = (e["result"], e["to"])
            if _k in _seen:
                continue
            _seen.add(_k)
            if any(x["result"] == e["result"] for x in tgt):
                continue
            tgt.append({"result": e["result"], "to": e["to"], "type": e["type"]})'''
assert old2 in s
s = s.replace(old2, new2, 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("已修正判定取用与去重")
