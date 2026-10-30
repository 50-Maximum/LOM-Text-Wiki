# -*- coding: utf-8 -*-
"""①青城-青城山镇 挂到青城山 ②无上级地点归入「其他」筛选档"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"

P = B + r"\data\places_fix.json"
d = json.load(open(P, encoding="utf-8"))
par = d.setdefault("parent", {})
par["青城-青城山镇"] = "青城山"
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("parent: 青城-青城山镇 → 青城山（共 %d 条）" % len(par))

S = B + r"\src\build_wiki2.py"
s = open(S, encoding="utf-8").read()
a = '_facet_pl = PPARENT.get(name) or ""'
b = '_facet_pl = PPARENT.get(name) or "其他"'
assert a in s, "facet 行未命中"
s = s.replace(a, b)
s = s.replace('facet=(PPARENT.get(_nm2) or ""))', 'facet=(PPARENT.get(_nm2) or "其他"))')
open(S, "w", encoding="utf-8").write(s)
print("build_wiki2: 无上级地点归入「其他」")
