# -*- coding: utf-8 -*-
"""找 scenes 定义位置与页面主循环起点，准备把地点-场景索引挪过去。"""
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
s = open(r"D:\LegendOfMortal Wiki\src\build_wiki2.py", encoding="utf-8").read()
for pat in ("scenes = ", "for typ, name in", "byname =", "SCENES_BY_PLACE = {}"):
    print("===", pat)
    for m in list(re.finditer(re.escape(pat), s))[:6]:
        ln = s[: m.start()].count("\n") + 1
        print("   L%-5d %s" % (ln, s[m.start():s.find("\n", m.start())][:100]))
