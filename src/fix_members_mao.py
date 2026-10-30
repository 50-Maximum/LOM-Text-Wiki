# -*- coding: utf-8 -*-
"""1) 成员判定改用实际前缀（含 PREFIX_FIX）；2) 清掉旧 intros 里的 毛二壮。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"

s = open(p, encoding="utf-8").read().replace("\r\n", "\n")
old = """        _mem = []
        for (_t, _n) in list(byname):
            if _t != "人物":
                continue
            _f = faction_of.get(_n)
            if not _f or FAC_NORM.get(_f, _f) != name:
                continue"""
new = """        _mem = []
        for (_t, _n) in list(byname):
            if _t != "人物":
                continue
            _pfx3 = char_prefix(_n)[0]
            if not _pfx3 or FAC_NORM.get(_pfx3, _pfx3) != name:
                continue"""
if old in s:
    s = s.replace(old, new, 1)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("成员判定已改为按前缀匹配")
else:
    print("未匹配到成员判定代码块")

q = os.path.join(B, "intros.json")
d = json.load(open(q, encoding="utf-8"))
hits = [k for k in d if "毛二壮" in k]
for k in hits:
    d.pop(k)
if hits:
    json.dump(d, open(q, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("intros.json 删除键:", hits or "无")
