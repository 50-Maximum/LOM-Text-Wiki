# -*- coding: utf-8 -*-
"""1) 额外势力页补「本派成员」栏；2) 成员列表滤掉「全真道兄」这类泛称。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")

# 1) 泛称过滤
old1 = """            if _dn3 in _ROLEWORDS:
                continue"""
new1 = """            if _dn3 in _ROLEWORDS:
                continue
            if _dn3.endswith(("弟子", "道兄", "师兄", "师弟", "师姐", "师妹",
                              "长老", "掌门", "护法", "帮众", "门人", "师兄们")) and len(_dn3) <= 7:
                continue"""
if old1 in s:
    s = s.replace(old1, new1, 1)
    print("泛称过滤已加")
else:
    print("未找到泛称过滤点")

# 2) 额外势力页补成员栏
old2 = """    _finf = {"类型": "势力", "提及": "0 条"}
    if _fpar:
        _finf["上级"] = _fpar
    add_page(_fslug, "势力", _fn, _fm.get("text") or "", _finf, [], ["势力"], 0, [],
             facet=(_fpar or "顶层"))"""
new2 = """    _finf = {"类型": "势力", "提及": "0 条"}
    if _fpar:
        _finf["上级"] = _fpar
    _fsecs = []
    _fmem = []
    for _cn in list(EXTRA_PE) + [k.split("/", 1)[1] for k in INTROS if k.startswith("人物/")]:
        _pf, _dn = char_prefix(_cn)
        if not _pf or FAC_NORM.get(_pf, _pf) != _fn:
            continue
        if _dn in _ROLEWORDS:
            continue
        _tt = char_title.get(_cn) or ""
        _fmem.append((_cn, ("「" + _tt + "」") if _tt else ""))
    if _fpar:
        _fsecs.append({"h": "上级势力", "rows": [
            {"note": _fpar, "quote": "", "script": "", "title": _fpar, "seq": 0, "routes": []}]})
    if _fmem:
        _fmem.sort()
        _finf["成员"] = f"{len(_fmem)} 人"
        _fsecs.append({"h": "本派成员（%d 人）" % len(_fmem), "rows": [
            {"note": (_a + ("｜" + _b)) if _b else _a, "quote": "", "script": "",
             "title": _a, "seq": 0, "routes": []} for _a, _b in _fmem]})
    add_page(_fslug, "势力", _fn, _fm.get("text") or "", _finf, _fsecs, ["势力"], 0, [],
             facet=(_fpar or "顶层"))"""
if old2 in s:
    s = s.replace(old2, new2, 1)
    print("额外势力页成员栏已加")
else:
    print("未找到额外势力页代码块")

open(p, "w", encoding="utf-8", newline="\n").write(s)
