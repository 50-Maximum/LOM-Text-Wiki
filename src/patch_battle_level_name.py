# -*- coding: utf-8 -*-
"""战斗行显示关卡名：用 ChangeScene 的关卡编号对到 CombatLevel/BattleLevel 描述。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

if "BATTLE_LV" not in s:
    anchor = "BATTLE_RESULTS = {}"
    add = '''BATTLE_LV = {}
try:
    _blv = os.path.join(BASE, "data", "battle_level_map.json")
    if os.path.exists(_blv):
        BATTLE_LV = json.load(open(_blv, encoding="utf-8"))
except Exception:
    BATTLE_LV = {}

BATTLE_RESULTS = {}'''
    assert anchor in s
    s = s.replace(anchor, add, 1)

old = '''        for _r in c.execute("""select dst,type,cond,switch,result,site from scene_edges
                               where src=? order by type, site, result""", (script,)):
            _dst, _ty, _cond, _sw, _res, _site = _r'''
new = '''        for _r in c.execute("""select dst,type,cond,switch,result,site,line from scene_edges
                               where src=? order by type, site, result""", (script,)):
            _dst, _ty, _cond, _sw, _res, _site, _ln = _r'''
assert old in s
s = s.replace(old, new, 1)

old2 = '''            elif _ty == "scene" and (_dst.startswith("Combat") or _dst.startswith("Battle")):
                _lab = "战斗：" + _dst'''
new2 = '''            elif _dst.startswith(("Combat", "Battle")):
                _blv2 = BATTLE_LV.get("%s|%s" % (script, _ln)) or {}
                _lab = "战斗：" + (_blv2.get("desc") or (("关卡 " + _blv2["id"]) if _blv2.get("id") else _dst))'''
assert old2 in s
s = s.replace(old2, new2, 1)

open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("战斗关卡名已接入")
