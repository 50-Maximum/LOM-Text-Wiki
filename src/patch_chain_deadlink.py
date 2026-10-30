# -*- coding: utf-8 -*-
"""剧情衔接栏去死链：指向非场景节点（Free/Combat/Title…）时不给脚本，只给语义标签。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

old = '''def chain_rows(script):
    """上一场 / 紧接着 / 分支去向（来自剧本 SetNextScript）。"""
    rows = []'''
new = '''_TGT_LBL = {"Free": "回养成地图（自由行动）", "Combat": "战斗", "Battle": "战役",
            "Title": "回标题画面", "GameOver": "结局", "Story": "剧情", "End": "结束",
            "section_01_free_start_01": "第一章养成段入口", "section_02_free_start_01": "第二章养成段入口"}


def _tgt_name(t):
    return scenes.get(t, {}).get("title") or _TGT_LBL.get(t) or t


def _tgt_scr(t):
    return t if t in scenes else ""


def chain_rows(script):
    """上一场 / 紧接着 / 分支去向（来自剧本 SetNextScript）。"""
    rows = []'''
assert old in s
s = s.replace(old, new, 1)

old2 = '''        rows.append({"note": "前一场：" + (scenes.get(src, {}).get("title") or src),
                     "quote": "", "script": src,
                     "title": scenes.get(src, {}).get("title") or src, "seq": 0, "routes": []})'''
new2 = '''        rows.append({"note": "前一场：" + _tgt_name(src),
                     "quote": "", "script": _tgt_scr(src),
                     "title": _tgt_name(src), "seq": 0, "routes": []})'''
assert old2 in s
s = s.replace(old2, new2, 1)

old3 = '''        rows.append({"note": "紧接着：" + (scenes.get(nx, {}).get("title") or nx),
                     "quote": "", "script": nx,
                     "title": scenes.get(nx, {}).get("title") or nx, "seq": 0, "routes": []})'''
new3 = '''        rows.append({"note": "紧接着：" + _tgt_name(nx),
                     "quote": "", "script": _tgt_scr(nx),
                     "title": _tgt_name(nx), "seq": 0, "routes": []})'''
assert old3 in s
s = s.replace(old3, new3, 1)

open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("剧情衔接去死链已接入")
