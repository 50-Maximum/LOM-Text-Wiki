# -*- coding: utf-8 -*-
"""① 给选项解析补上 "文案|条件" 表（骰子/菜单通用）；② 先做一次干跑统计能补多少。"""
import io, os, re, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "scripts")

RX_ANY = re.compile(r'(\w+)\[(\d+)\]\s*=\s*"([^"|]*)\|([^"]*)"')

fill = 0
files = 0
samples = []
for fn in os.listdir(RAW):
    if not fn.endswith(".txt"):
        continue
    s = open(os.path.join(RAW, fn), encoding="utf-8", errors="replace").read()
    tabs = collections.defaultdict(dict)
    for m in RX_ANY.finditer(s):
        txt = m.group(3).strip().lstrip("~")
        if txt:
            tabs[m.group(1)][m.group(2)] = (txt, m.group(4))
    if tabs:
        files += 1
        for t, d in tabs.items():
            fill += len(d)
        if len(samples) < 6:
            samples.append((fn, dict(list(tabs.items())[:2])))
print("含「文案|条件」表的脚本 %d 个，可解析选项 %d 条" % (files, fill))
for fn, t in samples:
    print("  %s %s" % (fn, t))
