# -*- coding: utf-8 -*-
"""①软件从哪里读 web 目录 ②筛选按钮/列表函数怎么写的"""
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"

print("=== app.py 里 web/静态目录")
for fn in ("src\\app.py", "src\\desktop.py"):
    p = os.path.join(B, fn)
    for i, ln in enumerate(open(p, encoding="utf-8", errors="replace")):
        if re.search(r"(web|static|MEIPASS|_MEIPASS|os\.path\.join|directory=)", ln):
            print("  %-14s %4d| %s" % (fn, i + 1, ln.strip()[:120]))

print("\n=== wiki.html 里 facet / 筛选相关")
h = open(os.path.join(B, "web", "wiki.html"), encoding="utf-8", errors="replace").read().split("\n")
for i, ln in enumerate(h):
    if re.search(r"(facet|FACET|setF|filter)", ln):
        print("  %4d| %s" % (i + 1, ln.strip()[:140]))
