# -*- coding: utf-8 -*-
"""扫描页面标题/正文里的繁体字残留（用 OpenCC t2s 比对，变了就是有繁体）。"""
import io, sys, sqlite3
from opencc import OpenCC
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
CC = OpenCC("t2s")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

bad = []
for slug, typ, name in c.execute("select slug,type,name from pages"):
    if name and CC.convert(name) != name:
        bad.append((typ, name, CC.convert(name)))
print("标题含繁体 %d 条" % len(bad))
from collections import Counter
print(Counter(t for t, _, _ in bad).most_common())
for t, a, b in bad[:25]:
    print("   %-6s %s → %s" % (t, a, b))

# 正文抽样
n = 0
for slug, typ, sec in c.execute("select slug,type,sections from pages where type='场景' limit 400"):
    if sec and CC.convert(sec) != sec:
        n += 1
print("\n场景页正文含繁体（前 400 条中）：%d" % n)
