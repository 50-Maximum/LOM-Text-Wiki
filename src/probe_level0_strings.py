# -*- coding: utf-8 -*-
"""看 level0 里 EnemyTeam 附近的原始数据形态：是不是「键 + 中文名」表。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data\level0"
b = open(P, "rb").read()
N = b"EnemyTeam"
idx, start = [], 0
while True:
    i = b.find(N, start)
    if i < 0:
        break
    idx.append(i)
    start = i + 1
print("出现次数", len(idx), "文件大小", len(b))
for k in idx[:6]:
    seg = b[max(0, k - 120): k + 220]
    txt = seg.decode("utf-8", "replace")
    print("\n--- 位置 %d ---" % k)
    print(repr(txt))
