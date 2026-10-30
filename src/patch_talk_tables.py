# -*- coding: utf-8 -*-
"""补解析 talk 菜单表：talk[N] = "exit/talk+文案+0+0" 或 Talk_Option_xx and "..." or "~x"。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_branch_tree.py"
s = open(P, encoding="utf-8").read()

if "RX_TALK" not in s:
    old = 'RX_TAB2 = re.compile(r\'(\\w+)\\[(\\d+)\\]\\s*=\\s*"([^"|]*)\\|([^"]*)"\')'
    assert old in s, "锚点1"
    s = s.replace(old, old + "\nRX_TALK = re.compile(r'(\\w+)\\[(\\d+)\\]\\s*=\\s*(?:[\\w.]+\\s+and\\s+)?\"([^\"]*)\"')", 1)

    old2 = """    sw_vars = {m.group(1): m.group(2) for m in RX_SWITCH.finditer(s)}"""
    assert old2 in s, "锚点2"
    new2 = """    for m in RX_TALK.finditer(s):
        _nm, _ix, _val = m.group(1), int(m.group(2)), m.group(3).strip()
        if not _val:
            continue
        if "+" in _val:
            _parts = _val.split("+")
            _kind = _parts[0].strip()
            _lab = (_parts[1].strip() if len(_parts) > 1 else "").strip()
            if _kind == "exit":
                continue          # 结束对话的入口，不算选项
            if _lab:
                menu_tabs[_nm].setdefault(_ix, _lab)
        elif _val != "~x":
            menu_tabs[_nm].setdefault(_ix, _val)
    sw_vars = {m.group(1): m.group(2) for m in RX_SWITCH.finditer(s)}"""
    s = s.replace(old2, new2, 1)
    open(P, "w", encoding="utf-8").write(s)
    py_compile.compile(P, doraise=True)
    print("build_branch_tree 已补 talk 表")
else:
    print("已存在 RX_TALK")
