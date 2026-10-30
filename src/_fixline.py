# -*- coding: utf-8 -*-
p = r"D:\LegendOfMortal Wiki\src\patch_cond_pages.py"
s = open(p, encoding="utf-8").read()
old = 'if "条件/{" not in s:'
new = 'if \'add_page("条件/"\' not in s:'
if old in s:
    s = s.replace(old, new)
    open(p, "w", encoding="utf-8").write(s)
    print("已修正判断条件")
else:
    print("已是新写法")
