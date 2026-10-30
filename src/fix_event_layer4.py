# -*- coding: utf-8 -*-
"""事件页选项：参数中文化、用 branch_options 补去向使选项可点、去掉开局噪声。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read().replace("\r\n", "\n")

# 1) 选项去向查表
if "BOPT_MAP" not in s:
    anchor = "def choice_rows(scs):"
    blk = ('# 选项文案 → 去向（补足 choice_branch 里缺失的 next）\n'
           'BOPT_MAP = {}\n'
           'try:\n'
           '    for _bs, _bv in (BRANCH_OPT or {}).items():\n'
           '        for _bg in _bv.get("groups") or []:\n'
           '            for _bo in _bg.get("options") or []:\n'
           '                if _bo.get("next"):\n'
           '                    BOPT_MAP[(_bs, (_bo.get("text") or "").strip())] = _bo["next"]\n'
           'except Exception as _e:\n'
           '    print("选项去向表跳过:", _e)\n\n\n')
    s = s.replace(anchor, blk + anchor, 1)
    print("BOPT_MAP 已插入")

# 2) 缺 next 时查表
old = '''                _nx = o.get("next") or _meta.get("next") or ""'''
new = '''                _nx = o.get("next") or _meta.get("next") or ""
                if not _nx:
                    _nx = BOPT_MAP.get((s, (o.get("text") or "").strip())) or ""'''
if old in s:
    s = s.replace(old, new, 1)
    print("选项去向补全已接入")

# 3) 结果里的英文参数转中文
old2 = '''                if o.get("effects"):
                    res.append("、".join(o["effects"]))'''
new2 = '''                if o.get("effects"):
                    res.append(stat_cn("、".join(o["effects"])))
                if o.get("result"):
                    pass'''
s = s.replace(old2, new2, 1)

# 4) 结果字符串整体过一遍中文表
old3 = '''                             "result": "；".join(res) or "—",'''
new3 = '''                             "result": stat_cn("；".join(res) or "—"),'''
if old3 in s:
    s = s.replace(old3, new3, 1)
    print("结果参数已中文化")

# 5) 开局限定行只在开局事件保留
old4 = '''                      and not (_fidx < _late and ("武林盟" in (r.get("note") or "")
                                                  or "西武林" in (r.get("note") or "")))]'''
new4 = '''                      and not (_fidx < _late and ("武林盟" in (r.get("note") or "")
                                                  or "西武林" in (r.get("note") or "")))
                      and not (_fidx != 0 and "游戏开始自动触发" in (r.get("note") or ""))]'''
if old4 in s:
    s = s.replace(old4, new4, 1)
    print("开局噪声已按阶段过滤")

open(P, "w", encoding="utf-8", newline="\n").write(s)
print("done")
