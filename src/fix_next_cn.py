# -*- coding: utf-8 -*-
"""把选项去向里的 Free/Battle 等系统名换成中文说法。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(p, encoding="utf-8").read().replace("\r\n", "\n")

helper = '''
SYS_NEXT_CN = {
    "Free": "养成地图（自由行动）",
    "Title": "标题画面",
    "Battle": "战斗",
    "Combat": "战斗",
    "End": "终章",
    "Story": "正篇",
    "GameOver": "游戏结束",
}


def next_cn(nx):
    return SYS_NEXT_CN.get(nx or "", (scenes.get(nx or "", {}) or {}).get("title") or (nx or ""))

'''
if "SYS_NEXT_CN" not in s:
    s = s.replace("def choice_rows(scs):", helper + "def choice_rows(scs):", 1)

old = '''                if _nx == "Title":
                    res.append("结束本段，回到标题")'''
new = '''                if _nx in SYS_NEXT_CN:
                    res.append("选择后转往" + SYS_NEXT_CN[_nx])'''
if old in s:
    s = s.replace(old, new, 1)

old2 = '''                             "next_title": (("结束本段（回标题）" if _nx == "Title"
                                             else scenes.get(_nx, {}).get("title") or _nx)
                                            if _nx else "")})'''
new2 = '''                             "next_title": next_cn(_nx) if _nx else ""})'''
if old2 in s:
    s = s.replace(old2, new2, 1)

open(p, "w", encoding="utf-8", newline="\n").write(s)
print("系统去向已中文化")
