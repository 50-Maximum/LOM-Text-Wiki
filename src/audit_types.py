# -*- coding: utf-8 -*-
"""审查：势力/地点是否混淆，归属是否按「出现地」错判。"""
import sqlite3, sys, io, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== char_faction 结构 ==")
for r in c.execute("select sql from sqlite_master where name='char_faction'"):
    print(r[0])
print("行数", c.execute("select count(*) from char_faction").fetchone()[0])

print()
print("== 势力名 vs 地名后缀 ==")
PLACE = ("山", "镇", "城", "村", "院", "堂", "房", "街", "店", "庄", "谷", "洞", "林",
         "寺", "观", "塔", "桥", "渡", "楼", "阁", "宫", "殿", "祠", "墓", "岛", "湖",
         "江", "河", "关", "岭", "峰", "崖", "泉", "井", "巷", "园", "府", "营", "寨")
for typ in ("势力", "地点"):
    print(f"-- {typ} --")
    rows = c.execute("select name,mentions from entities where type=? order by mentions desc", (typ,)).fetchall()
    for name, m in rows:
        suffix = name[-1]
        looks_place = suffix in PLACE
        if (typ == "势力" and looks_place) or (typ == "地点" and not looks_place):
            print(f"   ? {name} ({m})")

print()
print("== factions 表全部 ==")
for r in c.execute("select name,kind from factions order by name"):
    print(f"   {r[0]} ｜ {r[1] or ''}")
