# -*- coding: utf-8 -*-
"""核对地点归并与词条页。"""
import sqlite3, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

for slug in ("地点/崆峒山", "地点/唐门", "地点/锦香宫", "地点/风雨山", "地点/蜀中",
             "地点/岳阳", "地点/洞庭", "地点/外堡", "地点/唐门-外堡", "地点/破庙"):
    r = c.execute("select name,lead from pages where slug=?", (slug,)).fetchone()
    print(f"{slug:14} -> " + (f"{r[0]}｜{r[1][:60]}" if r else "（无）"))

print("\n唐门的下级：")
for r in c.execute("select dst,label from links where src='地点/唐门' and kind='下级'"):
    print("  ", r[1] or r[0])
print("崆峒山的下级：")
for r in c.execute("select dst,label from links where src='地点/崆峒山' and kind='下级'"):
    print("  ", r[1] or r[0])

print("\n词条页抽样：")
for slug in ("物品/唐门暗器总纲", "武学/brother1", "装备/鞭炮", "天赋/自恋", "成就/砍死"):
    r = c.execute("select name,lead,type from pages where slug=?", (slug,)).fetchone()
    print("  ", slug, "->", r if not r else (r[0], r[2], r[1][:40]))
print("武学页：", [x[0] for x in c.execute("select name from pages where type='武学'")])
print("地点页数", c.execute("select count(*) from pages where type='地点'").fetchone()[0])
