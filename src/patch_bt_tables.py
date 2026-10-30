# -*- coding: utf-8 -*-
"""build_branch_tree：补解析「文案|条件」表（骰子表与菜单表都吃）。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_branch_tree.py"
s = open(P, encoding="utf-8").read()

if "RX_TAB2" not in s:
    old = "RX_MENU_TAB = re.compile(r'(\\w+)\\[(\\d+)\\]\\s*=\\s*\"([^\"|]*)\"')"
    assert old in s, "锚点缺失"
    s = s.replace(old, old + "\nRX_TAB2 = re.compile(r'(\\w+)\\[(\\d+)\\]\\s*=\\s*\"([^\"|]*)\\|([^\"]*)\"')", 1)

    old2 = """    menu_tabs = collections.defaultdict(dict)
    for m in RX_MENU_TAB.finditer(s):
        menu_tabs[m.group(1)].setdefault(int(m.group(2)), m.group(3))"""
    assert old2 in s, "锚点2缺失"
    new2 = """    for m in RX_TAB2.finditer(s):
        _nm, _ix, _tx, _cd = m.group(1), int(m.group(2)), m.group(3).strip(), m.group(4)
        if not _tx:
            continue
        if "dice" in _nm.lower():
            dice_tabs[_nm].setdefault(_ix, (_tx, _cd))
            tab_pos[_nm].append(m.start())
    menu_tabs = collections.defaultdict(dict)
    for m in RX_MENU_TAB.finditer(s):
        menu_tabs[m.group(1)].setdefault(int(m.group(2)), m.group(3))
    for m in RX_TAB2.finditer(s):
        _nm, _ix, _tx = m.group(1), int(m.group(2)), m.group(3).strip()
        if _tx and "dice" not in _nm.lower():
            menu_tabs[_nm].setdefault(_ix, _tx)"""
    s = s.replace(old2, new2, 1)
    open(P, "w", encoding="utf-8").write(s)
    py_compile.compile(P, doraise=True)
    print("build_branch_tree 已支持文案|条件表")
else:
    print("已存在")
