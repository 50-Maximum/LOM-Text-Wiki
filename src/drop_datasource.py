# -*- coding: utf-8 -*-
"""删掉首页「数据从哪来」一段。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\web\wiki.html"
s = open(P, encoding="utf-8").read()

a = "  h+='<h2>数据从哪来</h2>'"
i = s.find(a)
if i < 0:
    print("未找到段落")
else:
    j = s.find("  h+='<details>", i)
    if j < 0:
        j = s.find("  h+='<h2>维护与反馈</h2>'", i)
    s = s[:i] + s[j:]
    open(P, "w", encoding="utf-8").write(s)
    print("已删除「数据从哪来」整段")
