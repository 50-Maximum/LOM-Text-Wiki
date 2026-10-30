# -*- coding: utf-8 -*-
"""看攻略里的事件卡片长什么样：提取 h3/卡片标题。"""
import io, re, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
D = r"D:\攻略"
for fn in ["特殊事件.html", "一次性事件.html", "重复性事件.html"]:
    p = os.path.join(D, fn)
    t = open(p, encoding="utf-8", errors="replace").read()
    body = t[t.find("<body"):]
    heads = re.findall(r"<h[23][^>]*>(.*?)</h[23]>", body, re.S)
    heads = [re.sub(r"<[^>]+>", "", h).strip() for h in heads]
    print("\n===", fn, "标题数", len(heads))
    for h in heads[:22]:
        print("   ", h)
