# -*- coding: utf-8 -*-
"""打印场景页生成处的上下文。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
s = open(r"D:\LegendOfMortal Wiki\src\build_wiki2.py", encoding="utf-8").read()
i = s.find('add_page(slug, "场景"')
print(s[max(0, i - 900):i + 260])
