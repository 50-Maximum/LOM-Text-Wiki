# -*- coding: utf-8 -*-
"""检查首页渲染结果：关键区块是否到位、旧内容是否已移除。"""
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
h = open(r"D:\LegendOfMortal Wiki\_home.html", encoding="utf-8", errors="replace").read()
for k in ["活侠传追踪Wiki", "从这里开始", "全文检索", "大地图", "时间线", "全部条目",
          "页面上的标注怎么读", "数据从哪来", "已知局限", "维护与反馈", "914717666",
          "修订建议", "登场最多的人物", "世界观"]:
    print("%-12s %s" % (k, "有" if k in h else "无"))
m = re.search(r"<h1>(.*?)</h1>", h)
print("\n标题:", m.group(1) if m else "-")
i = h.find('<div class="wrap">')
print("\n首屏文本:", re.sub(r"<[^>]+>", " ", h[i:i + 700]))
