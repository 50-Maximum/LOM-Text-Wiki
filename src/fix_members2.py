# -*- coding: utf-8 -*-
"""势力页成员：把 intros 里的人物也算进去，并滤掉「全真弟子」这类占位称谓。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")

old = """        _mem = []
        for (_t, _n) in list(byname):
            if _t != "人物":
                continue
            _pfx3 = char_prefix(_n)[0]
            if not _pfx3 or FAC_NORM.get(_pfx3, _pfx3) != name:
                continue
            _d2 = char_title.get(_n) or ""
            _mem.append((_n, (("「" + _d2 + "」") if _d2 else "")))
        for _n3, _m3 in EXTRA_PE.items():
            _f3 = (_m3 or {}).get("faction") or ""
            if FAC_NORM.get(_f3, _f3) != name:
                continue
            if any(x[0] == _n3 for x in _mem):
                continue
            _d2 = char_title.get(_n3) or ""
            _mem.append((_n3, (("「" + _d2 + "」") if _d2 else "")))"""

new = """        _mem = []
        _seen = set()
        _cand = [n for (t, n) in byname if t == "人物"]
        _cand += [k.split("/", 1)[1] for k in INTROS if k.startswith("人物/")]
        _cand += list(EXTRA_PE)
        for _n in _cand:
            if _n in _seen:
                continue
            _pfx3, _dn3 = char_prefix(_n)
            if not _pfx3 or FAC_NORM.get(_pfx3, _pfx3) != name:
                continue
            if _dn3 in _ROLEWORDS:
                continue
            _seen.add(_n)
            _d2 = char_title.get(_n) or ""
            _mem.append((_n, (("「" + _d2 + "」") if _d2 else "")))"""

if old in s:
    s = s.replace(old, new, 1)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("成员计算已更新（含 intros 人物、滤占位称谓）")
else:
    print("未匹配到成员计算块")
