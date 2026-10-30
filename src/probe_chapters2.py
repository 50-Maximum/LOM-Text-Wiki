# -*- coding: utf-8 -*-
"""章节盘点 + 末章场景（找结局分支）。"""
import os, sys, io, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== 章节分布 ==")
for r in c.execute("""select chapter, count(*), sum(line_count)
                      from scenes group by chapter order by chapter"""):
    print(f"  {r[0]:8} 场景 {r[1]:5}  台词 {r[2] or 0}")

print("\n== 第7、8章场景（按 script 排序，只列 >=8 句的）==")
for ch in ("第7章", "第8章"):
    print(f"\n--- {ch}")
    for r in c.execute("""select script,title,line_count from scenes
                          where chapter=? and line_count>=8 order by script""", (ch,)):
        print(f"  {r[0]:28} {r[2]:4}  {r[1]}")
