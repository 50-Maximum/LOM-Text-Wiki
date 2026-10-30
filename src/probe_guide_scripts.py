# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
for f in ("全事件索引.txt", "一次性事件.txt", "主线攻略.txt", "特殊事件.txt", "重复性事件.txt"):
    t = open(r"D:\LegendOfMortal Wiki\data\guide\\" + f, encoding="utf-8", errors="replace").read()
    print("%-16s 字%7d  游戏脚本:%3d  S\\d:%4d  ch\\d:%4d" % (
        f, len(t), t.count("游戏脚本"), len(re.findall(r"\bS\d{3,4}", t)), len(re.findall(r"\bch\d", t))))
# 看 全事件索引 一个块的完整结构
t = open(r"D:\LegendOfMortal Wiki\data\guide\全事件索引.txt", encoding="utf-8", errors="replace").read()
i = t.find("触发条件")
print("\n首个触发条件上下文:\n", t[max(0, i - 400): i + 400])
