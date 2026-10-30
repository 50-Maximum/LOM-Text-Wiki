# -*- coding: utf-8 -*-
"""检测 lines 表里仍是繁体的台词。"""
import sqlite3, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

TRAD = set("們個這來說時會為與對開關後裡麼樣經過還進發現實點兒東頭體當學國無龍劍術門"
           "價買賣錢鐵銀銅鏡標準變讓從聽寫讀語話認識見到處邊遠近長短高矮強弱勝敗勝負")
# 简化字里不会出现的高频繁体字
HOT = "們這個說時會為與對開關後裡麼樣經過還進發現實點東頭體當學國無龍劍術門價買賣錢鐵銀"

def is_trad(s):
    hit = [ch for ch in s if ch in HOT]
    return len(hit) >= 2 or (hit and len(hit) / max(1, len(s)) > 0.08)

rows = c.execute("select id, script, seq, speaker, text from lines").fetchall()
trad = [(i, s, q, sp, t) for i, s, q, sp, t in rows if t and is_trad(t)]
print("疑似繁体台词", len(trad), "/", len(rows))
for r in trad[:15]:
    print(f"   {r[1]} #{r[2]} {r[3]}: {r[4][:50]}")

# 按脚本统计
from collections import Counter
cnt = Counter(s for _, s, _, _, _ in trad)
print()
print("涉及脚本", len(cnt))
for s, n in cnt.most_common(10):
    print("   ", s, n)
