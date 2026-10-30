# -*- coding: utf-8 -*-
"""定位 build_wiki2 里地点页生成、下辖地点链接、势力页生成的代码位置。"""
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(S, encoding="utf-8").read()
pats = ["下辖地点", "PPARENT", "places_fix", "地点/", "势力/", "add_page("]
for pat in pats:
    print("=== %s" % pat)
    for m in list(re.finditer(re.escape(pat), s))[:10]:
        ln = s[: m.start()].count("\n") + 1
        line = s[s.rfind("\n", 0, m.start()) + 1: s.find("\n", m.start())]
        print("  L%-5d %s" % (ln, line.strip()[:110]))
