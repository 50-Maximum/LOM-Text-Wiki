# -*- coding: utf-8 -*-
"""旗标语义：路线/结局相关。"""
import os, sys, io, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== flaginfo 里含关键词的 ==")
for kw in ("结局", "路线", "线", "攻略", "留学", "盟主", "武林", "称帝", "死"):
    rows = c.execute("select flag,label from flaginfo where label like ? limit 12", (f"%{kw}%",)).fetchall()
    if rows:
        print(f"\n-- {kw}")
        for r in rows:
            print("   ", r[0], r[1])

print("\n== 前缀分布 ==")
cnt = collections.Counter()
for (f,) in c.execute("select flag from flaginfo"):
    cnt[f[0]] += 1
print("  ", dict(cnt))

print("\n== G11 / M / E 开头全部 ==")
for r in c.execute("select flag,label from flaginfo where flag like 'G11%' or flag like 'M2%' or flag like 'M4%' or flag like 'M6%' or flag like 'M7%' or flag like 'E12%' order by flag"):
    print("  ", r[0], r[1])
