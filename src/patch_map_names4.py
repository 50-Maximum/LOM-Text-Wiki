# -*- coding: utf-8 -*-
"""统一命名呈现：剧本标题档若不含地点词，也补地点前缀。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

old = '''    else:
        title = (place + "・" + title) if (place and title_src == "原生标题") else title'''
new = '''    else:
        if place and place not in title:
            title = place + "・" + title'''
assert old in s
s = s.replace(old, new, 1)
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("命名呈现统一")
