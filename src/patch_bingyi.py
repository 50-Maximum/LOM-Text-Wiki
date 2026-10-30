# -*- coding: utf-8 -*-
"""给 build_wiki2 加两段收尾处理：①同名地点/势力并义；②补「眉山镇」子地点页。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(S, encoding="utf-8").read()

ANCHOR = 'c.executemany("insert or replace into pages values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", pages)'
assert ANCHOR in s, "pages 写入语句未找到"
if "_MERGE_EQ" in s:
    print("已存在收尾段，跳过")
    sys.exit()

BLOCK = '''
# ===== 收尾：并义（同名地点/势力共用内容）+ 补指定子地点 =====
_MERGE_EQ = []


def _pj(v, d):
    try:
        return json.loads(v or d)
    except Exception:
        return json.loads(d)


_idx = {p[0]: i for i, p in enumerate(pages)}
for _p in list(pages):
    if _p[1] != "地点":
        continue
    _b = f"势力/{_p[2]}"
    if _b in _idx:
        _a = _p[0]
        _pa, _pb = pages[_idx[_a]], pages[_idx[_b]]
        _sa, _sb = _pj(_pa[5], "[]"), _pj(_pb[5], "[]")
        _have = {x.get("h") for x in _sa}
        _merged = _sa + [x for x in _sb if x.get("h") not in _have]
        _ia, _ib = _pj(_pa[4], "{}"), _pj(_pb[4], "{}")
        for _k2, _v2 in _ib.items():
            _ia.setdefault(_k2, _v2)
        _ia["性质"] = "兼为地点与势力"
        _cats = sorted(set(_pj(_pa[6], "[]")) | set(_pj(_pb[6], "[]")))
        _mj = json.dumps(_merged, ensure_ascii=False)
        _ij = json.dumps(_ia, ensure_ascii=False)
        _cj = json.dumps(_cats, ensure_ascii=False)
        _mt = max(_pa[7] or 0, _pb[7] or 0)
        for _i in (_idx[_a], _idx[_b]):
            _q = pages[_i]
            pages[_i] = (_q[0], _q[1], _q[2], _q[3], _ij, _mj, _cj, _mt,
                         _q[8], _q[9], _q[10], _q[11], _q[12], _q[13])
        links.append((_a, _b, "同义", ""))
        links.append((_b, _a, "同义", ""))
        _MERGE_EQ.append(_a.split("/")[-1])
print("并义条目", len(_MERGE_EQ), "：", "、".join(_MERGE_EQ[:12]))

# 指定补充的子地点（有出处、但原文没有成段描写，需要单独成页）
_EXTRA_PLACES = [
    ("眉山镇", "眉山", "眉山镇是眉山山下的镇市，唐门弟子下山采买、坊市街巷多聚于此。"),
]
for _nm3, _par3, _lead3 in _EXTRA_PLACES:
    _slug3 = f"地点/{_nm3}"
    if _slug3 in _idx:
        continue
    _pslug = f"地点/{_par3}"
    if _pslug in _idx:
        _pp2 = pages[_idx[_pslug]]
        _ps = _pj(_pp2[5], "[]")
        _row = {"note": _nm3, "quote": "", "script": "", "title": _nm3,
                "slug": _slug3, "seq": 0, "routes": []}
        for _s in _ps:
            if _s.get("h") == "下辖地点":
                _s.setdefault("rows", []).append(_row)
                break
        else:
            _ps.append({"h": "下辖地点", "rows": [_row]})
        _pi = _pj(_pp2[4], "{}")
        _pi["下辖"] = f"{len([k for k, v in PPARENT.items() if v == _par3])} 处"
        pages[_idx[_pslug]] = (_pp2[0], _pp2[1], _pp2[2], _pp2[3],
                               json.dumps(_pi, ensure_ascii=False),
                               json.dumps(_ps, ensure_ascii=False),
                               _pp2[6], _pp2[7], _pp2[8], _pp2[9],
                               _pp2[10], _pp2[11], _pp2[12], _pp2[13])
        links.append((_slug3, _pslug, "上级", ""))
        links.append((_pslug, _slug3, "下级", _nm3))
    pages.append((_slug3, "地点", _nm3, _lead3,
                  json.dumps({"类型": "地点", "上级": _par3}, ensure_ascii=False),
                  "[]", json.dumps(["地点"], ensure_ascii=False), 0, "[]",
                  "", "", 0, _region_of(_nm3), "城镇"))
    _idx[_slug3] = len(pages) - 1
    print("新增地点页", _nm3, "→ 上级", _par3)

'''
s = s.replace(ANCHOR, BLOCK + "\n" + ANCHOR, 1)
open(S, "w", encoding="utf-8").write(s)
print("build_wiki2：已插入并义与补充地点段")
