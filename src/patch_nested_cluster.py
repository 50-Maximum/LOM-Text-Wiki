# -*- coding: utf-8 -*-
"""「择一分支」栏支持嵌套簇：外层与内层都显示，触顶截断的路线加说明。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

old = '''    _cl = CLUSTER_MAP.get(script)
    if _cl:
        _c = CLUSTER_BY_ID.get(_cl.get("cluster")) or {}
        _rows_c = [{"note": "本场属于「%s」判定 %s 的第 %s 路（结果 %s），与下列路线互斥，一次只走一条。"
                            % (scenes.get(_c.get("src"), {}).get("title") or _c.get("src") or "",
                               _c.get("switch") or "", _cl.get("alt"), "/".join(_cl.get("results") or [])),
                    "quote": "", "script": "", "title": "", "seq": 0, "routes": []}]
        for _i, _alt in enumerate(_c.get("alts") or [], 1):
            if _i == _cl.get("alt"):
                continue
            _t = scenes.get(_alt.get("entry"), {}).get("title") or _alt.get("entry")
            _rows_c.append({"note": "另一路（结果 %s）：%s　共 %d 场"
                                    % ("/".join(_alt.get("results") or []), _t, len(_alt.get("scenes") or [])),
                            "quote": "", "script": _alt.get("entry"), "title": _t,
                            "seq": 0, "routes": []})
        secs.append({"h": "择一分支", "rows": _rows_c})'''

new = '''    _cl = CLUSTER_MAP.get(script)
    if _cl:
        _mem = _cl.get("all") or [{"cluster": _cl.get("cluster"), "alt": _cl.get("alt"),
                                   "n": _cl.get("n"), "results": _cl.get("results")}]
        _rows_c = []
        for _k, _m in enumerate(_mem):
            _c = CLUSTER_BY_ID.get(_m.get("cluster")) or {}
            if not _c:
                continue
            _st = scenes.get(_c.get("src"), {}).get("title") or _c.get("src") or ""
            _head = ("本场属于「%s」判定 %s 的第 %s 路（结果 %s），与下列路线互斥，一次只走一条。"
                     % (_st, _c.get("switch") or "", _m.get("alt"),
                        "/".join(_m.get("results") or [])))
            if _k > 0:
                _head = "其中还嵌套一组分支：「%s」判定 %s，本场在第 %s 路（结果 %s）。" % (
                    _st, _c.get("switch") or "", _m.get("alt"), "/".join(_m.get("results") or []))
            _rows_c.append({"note": _head, "quote": "", "script": "", "title": "",
                            "seq": 0, "routes": []})
            for _i, _alt in enumerate(_c.get("alts") or [], 1):
                if _i == _m.get("alt"):
                    continue
                _t = scenes.get(_alt.get("entry"), {}).get("title") or _alt.get("entry")
                _tail = "（该路超长，仅列到 400 场）" if _alt.get("truncated") else ""
                _rows_c.append({"note": "另一路（结果 %s）：%s　共 %d 场%s"
                                        % ("/".join(_alt.get("results") or []), _t,
                                           len(_alt.get("scenes") or []), _tail),
                                "quote": "", "script": _alt.get("entry"), "title": _t,
                                "seq": 0, "routes": []})
        if _rows_c:
            secs.append({"h": "择一分支", "rows": _rows_c})'''

assert old in s
s = s.replace(old, new, 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("嵌套分支渲染已接入")
