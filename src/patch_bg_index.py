# -*- coding: utf-8 -*-
"""接背景资源：
① place_of 增加「背景资源（推断）」；
② 场景页 infobox 显示所用背景，并链到背景资源页；
③ 生成「背景资源」条目，列出使用该背景的所有场景。
"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(S, encoding="utf-8").read()

# ① 载入
if "PLACE_INFER5" not in s:
    anchor = 'PLACE_INFER4 = {}'
    i = s.find(anchor)
    j = s.find("PLACE_INFER4 = {}", s.find("except Exception:", i))
    j = s.find("\n", j) + 1
    add = '''
PLACE_INFER5 = {}
try:
    _pi5 = os.path.join(BASE, "data", "place_infer5.json")
    if os.path.exists(_pi5):
        PLACE_INFER5 = json.load(open(_pi5, encoding="utf-8"))
except Exception:
    PLACE_INFER5 = {}

SCENE_BG = {}
try:
    _bgp = os.path.join(BASE, "data", "scene_bg.json")
    if os.path.exists(_bgp):
        SCENE_BG = json.load(open(_bgp, encoding="utf-8"))
except Exception:
    SCENE_BG = {}
'''
    s = s[:j] + add + s[j:]
    print("已载入 PLACE_INFER5 / SCENE_BG")

if "PLACE_INFER5.get(script)" not in s:
    tail = '    _i4 = PLACE_INFER4.get(script) or {}'
    assert tail in s
    ins = '''    _i5 = PLACE_INFER5.get(script) or {}
    if _i5.get("place"):
        return pcanon(_i5["place"]), "背景资源（推断）"
'''
    s = s.replace(tail, ins + tail, 1)
    print("place_of 已接背景推断")

# ②③ 收尾：背景字段 + 背景资源页
if "_BG_DONE" not in s:
    anchor2 = 'c.executemany("insert or replace into pages values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", pages)'
    assert anchor2 in s
    block = '''# ===== 背景资源：场景页字段 / 背景资源条目 =====
_BG_DONE = 0
_BG_AGG = {}
for _i8, _q8 in enumerate(pages):
    if _q8[1] != "场景":
        continue
    _sc8 = _q8[0].split("/", 1)[1] if "/" in _q8[0] else _q8[0]
    _bgs = SCENE_BG.get(_sc8)
    if not _bgs:
        continue
    _inf8 = _pj(_q8[4], "{}")
    _inf8["背景"] = "、".join(_bgs[:4])
    pages[_i8] = (_q8[0], _q8[1], _q8[2], _q8[3], json.dumps(_inf8, ensure_ascii=False),
                  _q8[5], _q8[6], _q8[7], _q8[8], _q8[9], _q8[10], _q8[11],
                  _q8[12], _q8[13])
    for _b8 in _bgs:
        _BG_AGG.setdefault(_b8, []).append(_sc8)
        links.append((_q8[0], f"背景资源/{_b8}", "背景", _b8))
    _BG_DONE += 1

for _b8 in sorted(_BG_AGG):
    _scs8 = _BG_AGG[_b8]
    _rows8 = [{"note": scenes.get(_x8, {}).get("title") or _x8, "quote": "", "script": _x8,
               "title": scenes.get(_x8, {}).get("title") or _x8, "seq": 0, "routes": []}
              for _x8 in _scs8[:200]]
    add_page(f"背景资源/{_b8}", "背景资源", _b8,
             f"背景资源 {_b8}，共被 {len(_scs8)} 场剧情使用。",
             {"类型": "背景资源", "使用场景": f"{len(_scs8)} 场"},
             [{"h": "使用场景", "rows": _rows8}], ["背景资源"], len(_scs8), [])
print("背景字段", _BG_DONE, "页；背景资源条目", len(_BG_AGG), "个")

'''
    s = s.replace(anchor2, block + anchor2, 1)
    print("已插入背景资源收尾块")

open(S, "w", encoding="utf-8").write(s)
print("done")
