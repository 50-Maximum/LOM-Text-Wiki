# -*- coding: utf-8 -*-
"""给场景页加「分支选项」栏：选项原文 → 条件 → 去向。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")

# 1) 载入 branch_options.json
anchor = "def char_prefix(nm):"
if "BRANCH_OPT" not in s:
    load_block = (
        '# 分支选项（data/branch_options.json）\n'
        'BRANCH_OPT = {}\n'
        'try:\n'
        '    _bop = os.path.join(BASE, "data", "branch_options.json")\n'
        '    if os.path.exists(_bop):\n'
        '        BRANCH_OPT = json.load(open(_bop, encoding="utf-8"))\n'
        'except Exception as _e:\n'
        '    print("分支选项跳过:", _e)\n\n\n'
    )
    s = s.replace(anchor, load_block + anchor, 1)
    print("已插入 BRANCH_OPT 载入")

# 2) 场景页加栏
old = '    add_page(slug, "场景", sc.get("title") or script, _lead, inf, secs,'
new = ('''    _bo = BRANCH_OPT.get(script)
    if _bo:
        _brows = []
        for _g in _bo.get("groups") or []:
            if _g.get("prompt"):
                _brows.append({"note": "【本题】" + _g["prompt"][:110], "quote": "",
                               "script": "", "title": "", "seq": 0, "routes": []})
            for _o in _g.get("options") or []:
                _tgt = _o.get("next") or ""
                _note = "「%s」" % _o["text"]
                if _o.get("cond"):
                    _note += "　条件：" + _o["cond"]
                if _o.get("effects"):
                    _note += "　影响：" + "、".join(_o["effects"])
                if not _tgt:
                    _note += "　（去向未定）"
                _brows.append({"note": _note, "quote": "", "script": _tgt,
                               "title": _tgt, "seq": 0, "routes": []})
        if _brows:
            secs.append({"h": "分支选项", "rows": _brows})

''' + old)
if old in s:
    s = s.replace(old, new, 1)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("场景页已加「分支选项」栏")
else:
    print("未找到场景页 add_page 锚点")
