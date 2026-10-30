# -*- coding: utf-8 -*-
"""战斗标签改为只认结构证据（data/battle_results.json），无证据就不说胜负。"""
import io, re, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

# 1) 载入表
if "BATTLE_RESULTS" not in s:
    anchor = "def battle_label(sw, res):"
    add = '''BATTLE_RESULTS = {}
try:
    _brp = os.path.join(BASE, "data", "battle_results.json")
    if os.path.exists(_brp):
        BATTLE_RESULTS = json.load(open(_brp, encoding="utf-8"))
except Exception:
    BATTLE_RESULTS = {}


def battle_label(sw, res, script=""):'''
    assert anchor in s
    s = s.replace(anchor, add, 1)

# 2) 函数体：查结构表，查不到返回空
old_body = re.search(r'def battle_label\(sw, res, script=""\):.*?\n\ndef pretty_cond', s, re.S)
assert old_body, "找不到 battle_label 函数体"
new_func = '''def battle_label(sw, res, script=""):
    """胜负只按剧本结构判定（重打/GameOver=败，推进剧情=胜），查不到就不给标签。"""
    if not sw or not script:
        return ""
    mp = (BATTLE_RESULTS.get(script) or {}).get(sw) or {}
    lb = mp.get(str(res)) or ""
    if lb == "胜":
        return "战斗胜利"
    if lb == "败":
        return "战斗失败"
    return ""


def pretty_cond'''
s = s[:old_body.start()] + new_func + s[old_body.end():]

# 3) 调用点加 script
s = s.replace("_bl = battle_label(_sw, _res)", "_bl = battle_label(_sw, _res, script)", 1)
s = s.replace('if _ty == "branch" and not battle_label(_sw, _res):',
              'if _ty == "branch" and not battle_label(_sw, _res, script):', 1)

open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("战斗标签改为结构判定")
