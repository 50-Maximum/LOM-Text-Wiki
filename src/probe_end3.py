# -*- coding: utf-8 -*-
"""终章 epilogue 按条件分块，摘出每块开头几句。"""
import os, sys, io, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

rows = c.execute("""select seq,speaker,text,branch from lines
                    where script='ch8_8_1' order by seq""").fetchall()
groups = collections.OrderedDict()
for seq, sp, tx, br in rows:
    key = br or "（无条件）"
    groups.setdefault(key, []).append((seq, sp, (tx or "").replace("\n", " ")))

print("分支块", len(groups), "\n")
for key, arr in groups.items():
    if len(arr) < 3:
        continue
    print(f"\n### {key[:150]}")
    print(f"    共 {len(arr)} 句")
    for seq, sp, tx in arr[:4]:
        print(f"    {seq:4} {sp}：{tx[:96]}")
