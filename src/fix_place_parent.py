# -*- coding: utf-8 -*-
"""把具体地名纳入子级：眉山→唐门所在县镇；岷江/渡口/医馆挂眉山；都江客栈挂青城山镇。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\data\places_fix.json"
d = json.load(open(P, encoding="utf-8"))
par = d.setdefault("parent", {})
print("原 parent：", json.dumps(par, ensure_ascii=False)[:400])

ADD = {
    "唐门": "眉山",            # 眉山是唐门所在的县镇
    "岷江": "眉山",            # 赵活下山的江行水路
    "渡口": "眉山",
    "都江客栈": "青城-青城山镇",
}
for k, v in ADD.items():
    par[k] = v
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n新 parent：", json.dumps(par, ensure_ascii=False)[:500])
