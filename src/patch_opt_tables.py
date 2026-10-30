# -*- coding: utf-8 -*-
"""给 p1_parse 补上「文案|条件」选项表解析（骰子/菜单通用，条件是任意文本）。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\p1_parse.py"
s = open(P, encoding="utf-8").read()

if "RX_TAB2" not in s:
    old = '''RX_MENU_TAB = re.compile('(\\\\w+)\\\\[(\\\\d+)\\\\]\\\\s*=\\\\s*"([^"|]*)"')'''
    assert old in s, "锚点 RX_MENU_TAB 缺失"
    s = s.replace(old, old + '''
RX_TAB2 = re.compile('(\\\\w+)\\\\[(\\\\d+)\\\\]\\\\s*=\\\\s*"([^"|]*)\\\\|([^"]*)"')''', 1)

    old2 = '''        choice_var = {m.group(1): m.group(2) for m in RX_CHOICEVAR.finditer(s)}'''
    assert old2 in s
    s = s.replace(old2, '''        for m in RX_TAB2.finditer(s):
            _nm, _ix, _txt, _cd = m.group(1), m.group(2), m.group(3), m.group(4)
            if _txt.strip() and not (tables.get(_nm, {}).get(_ix) or {}).get("label"):
                tables[_nm][_ix] = {"raw": _txt.strip(),
                                    "label": _txt.strip().lstrip("~"), "cond": _cd}
''' + old2, 1)
    open(P, "w", encoding="utf-8").write(s)
    py_compile.compile(P, doraise=True)
    print("p1_parse 已支持「文案|条件」表")
else:
    print("已存在 RX_TAB2")
