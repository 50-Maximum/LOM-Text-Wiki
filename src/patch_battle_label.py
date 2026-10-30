# -*- coding: utf-8 -*-
"""把战斗结果边渲染成人话：判定 Combat_Result_02 结果 1 → 战斗胜利。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

# 1) 胜负映射辅助函数
if "def battle_label" not in s:
    anchor = "def pretty_cond(t):"
    add = '''def battle_label(sw, res):
    """战斗结果开关 → 胜利/失败。判定库：Combat_Result_02=C00000需1(胜)，01=需0(败)。"""
    if not sw:
        return ""
    try:
        r = int(res or 0)
    except Exception:
        r = 0
    if sw.startswith("Combat_Result"):
        win_res = 1 if sw.endswith("_02") else 2
    elif sw.startswith("Battle_Result"):
        win_res = 1 if sw.endswith("_001") else 2
    else:
        return ""
    return "战斗胜利" if r == win_res else "战斗失败"


'''
    assert anchor in s
    s = s.replace(anchor, add + anchor, 1)

# 2) 分支标签优先用战斗胜负
old = '''                if _ty == "branch":
                    _bits = []'''
new = '''                if _ty == "branch":
                    _bl = battle_label(_sw, _res)
                    if _bl:
                        _lab = _bl + "：" + (_title or _dst)
                if _ty == "branch" and not battle_label(_sw, _res):
                    _bits = []'''
assert old in s
s = s.replace(old, new, 1)

open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("战斗胜负标签已接入")
