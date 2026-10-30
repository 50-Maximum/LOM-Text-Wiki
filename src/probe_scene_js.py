# -*- coding: utf-8 -*-
"""看 lineHtml 是否带 data-seq，以及路由怎么传 scene 参数。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
s = open(r"D:\LegendOfMortal Wiki\web\wiki.html", encoding="utf-8").read()

i = s.find("function lineHtml")
print("=== lineHtml ===")
print(s[i:i + 800])

j = s.find("kind==='scene'")
print("\n=== 路由 scene 分支 ===")
print(s[max(0, j - 260):j + 120])
