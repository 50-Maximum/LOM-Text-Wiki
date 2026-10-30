# -*- coding: utf-8 -*-
"""看赵活简介原文，准备剔除只靠 Demo 练功塔支撑的说法。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\data\intros_char.json"
d = json.load(open(P, encoding="utf-8"))
e = d["人物/赵活"]
print("脚注：", json.dumps(e.get("footnotes"), ensure_ascii=False)[:600])
print("\n正文：\n", e["text"])
