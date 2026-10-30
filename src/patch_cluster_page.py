# -*- coding: utf-8 -*-
"""场景页加「择一分支」：本场属于哪条路线、与哪些路线互斥。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

# 1) 载入簇数据
if "CLUSTER_MAP" not in s:
    a = "COND_USED = {}\ntry:"
    i = s.find(a)
    j = s.find("\n", s.find("except Exception:", i))
    j = s.find("\n", j + 1) + 1
    s = s[:j] + '''
CLUSTERS = []
CLUSTER_BY_ID = {}
CLUSTER_MAP = {}
try:
    _clp2 = os.path.join(BASE, "data", "scene_clusters.json")
    if os.path.exists(_clp2):
        CLUSTERS = json.load(open(_clp2, encoding="utf-8"))
        CLUSTER_BY_ID = {x["id"]: x for x in CLUSTERS}
    _cmp = os.path.join(BASE, "data", "scene_cluster_map.json")
    if os.path.exists(_cmp):
        CLUSTER_MAP = json.load(open(_cmp, encoding="utf-8"))
except Exception:
    CLUSTERS = []
''' + s[j:]
    print("已载入分支簇")

# 2) 场景页追加栏目
if "择一分支" not in s:
    anchor = '    secs.append({"h": "接下来", "rows": _jrows})'
    assert anchor in s
    block = anchor + '''
    _cl = CLUSTER_MAP.get(script)
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
    s = s.replace(anchor, block, 1)
    print("场景页已加择一分支")

open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("syntax ok")
