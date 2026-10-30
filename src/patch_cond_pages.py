# -*- coding: utf-8 -*-
"""① 场景页加「接下来」去向；② 生成「条件」条目（判定库可搜可读）。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(S, encoding="utf-8").read()

# ---------- 1. 载入 cond_lib ----------
if "COND_LIB" not in s:
    a = "PLACE_INFER6 = {}"
    i = s.find(a)
    j = s.find("\n", s.find("except Exception:", i))
    j = s.find("\n", j + 1) + 1
    s = s[:j] + '''
COND_LIB = {}
try:
    _clp = os.path.join(BASE, "data", "cond_lib.json")
    if os.path.exists(_clp):
        COND_LIB = json.load(open(_clp, encoding="utf-8"))
except Exception:
    COND_LIB = {}
''' + s[j:]
    print("已载入 COND_LIB")

# ---------- 2. 场景页「接下来」 ----------
if '"h": "接下来"' not in s:
    a = '        secs.append({"h": "剧情衔接", "rows": _cr})'
    # 场景页那处（第一处出现在 1342 附近，先定位到含 _cr 的场景页）
    idx = s.find(a)
    assert idx > 0
    block = a + '''
    _nxt = (NXT.get(script) or {})
    _nx = _nxt.get("next")
    _jrows = []
    if _nx and _nx in scenes:
        _jrows.append({"note": "继续：" + (scenes.get(_nx, {}).get("title") or _nx),
                       "quote": "", "script": _nx,
                       "title": scenes.get(_nx, {}).get("title") or _nx, "seq": 0, "routes": []})
    for _e in (_nxt.get("edges") or [])[:8]:
        _t = _e.get("target") or ""
        if not _t or _t == _nx or _t not in scenes:
            continue
        _cnd = (_e.get("cond") or "").strip()
        _lab = ("分支：" + (scenes.get(_t, {}).get("title") or _t))
        if _cnd:
            _ids = [x for x in re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", _cnd) if x in COND_LIB]
            _lab += "（条件：" + _cnd.replace("switch", "判定").replace("_result==", " 判定结果=") + "）"
        _jrows.append({"note": _lab, "quote": "", "script": _t,
                       "title": scenes.get(_t, {}).get("title") or _t, "seq": 0, "routes": []})
    if not _jrows:
        _jrows.append({"note": "本场结束后没有后续脚本，通常回到地图（养成）或由上层事件接续。",
                       "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
    secs.append({"h": "接下来", "rows": _jrows})'''
    s = s.replace(a, block, 1)
    print("场景页已加「接下来」")

# ---------- 3. 条件条目 ----------
if 'add_page("条件/"' not in s:
    anchor = 'c.executemany("insert or replace into pages values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", pages)'
    assert anchor in s
    blk = '''# ===== 条件条目（判定库）=====
_COND_USED = {}
try:
    _tokre = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")
    for _r in c.execute("select script, cond from branch_nodes"):
        for _t in set(_tokre.findall(_r[1] or "")):
            if _t in COND_LIB:
                _COND_USED.setdefault(_t, set()).add(_r[0])
    for _r in c.execute("select script, options from choices"):
        for _t in set(_tokre.findall(_r[1] or "")):
            if _t in COND_LIB:
                _COND_USED.setdefault(_t, set()).add(_r[0])
    for _r in c.execute("select script, branch from branches"):
        for _t in set(_tokre.findall(_r[1] or "")):
            if _t in COND_LIB:
                _COND_USED.setdefault(_t, set()).add(_r[0])
except Exception as _e:
    print("条件反查失败", _e)

_cond_pages = 0
for _cid, _scs in _COND_USED.items():
    _info = COND_LIB.get(_cid) or {}
    _attrs = _info.get("attrs") or []
    _kind = "多路判定" if _info.get("kind") == "switch" else "条件表达式"
    _lead = "%s %s：%s" % (_kind, _cid, "；".join(_attrs)[:120])
    _rows = []
    for _i, _a in enumerate(_attrs, 1):
        _rows.append({"note": ("结果 %d：" % _i if _info.get("kind") == "switch" else "") + str(_a),
                      "quote": "", "script": "", "title": "", "seq": 0, "routes": []})
    _scrows = [{"note": scenes.get(_x, {}).get("title") or _x, "quote": "",
                "script": _x, "title": scenes.get(_x, {}).get("title") or _x,
                "seq": 0, "routes": []} for _x in sorted(_scs)[:60]]
    add_page("条件/" + _cid, "条件", _cid, _lead,
             {"类型": _kind, "结果数": len(_attrs), "引用场景": "%d 场" % len(_scs)},
             [{"h": "判定内容", "rows": _rows}, {"h": "用到这个判定的场景", "rows": _scrows}],
             ["条件"], len(_scs), [], facet=_kind)
    _cond_pages += 1
print("条件条目", _cond_pages, "个（判定库共", len(COND_LIB), "）")

'''
    s = s.replace(anchor, blk + anchor, 1)
    print("条件条目块已插入")

open(S, "w", encoding="utf-8").write(s)
import py_compile
py_compile.compile(S, doraise=True)
print("syntax ok")
