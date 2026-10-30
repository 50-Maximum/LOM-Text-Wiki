# -*- coding: utf-8 -*-
import sqlite3, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("===== 表 =====")
for r in c.execute("select name from sqlite_master where type='table' order by name"):
    print(r[0], end=" ｜ ")
print()

print("\n===== 地点页（顶层/子页） =====")
try:
    kids = {r[0] for r in c.execute("select slug from place_children")}
    for r in c.execute("select slug,json_extract(infobox,'$.上级') up,mentions from pages where type='地点' order by slug"):
        mark = "子" if r[0] in kids else "顶"
        print(f"{mark} {r[0]} 上级={r[1]} 提及={r[2]}")
except Exception as e:
    print("err", e)

print("\n===== 含眉山/唐门的地名 =====")
for r in c.execute("select distinct place from scenes where place like '%眉山%' or place like '%唐门%' limit 30"):
    print(r[0], end=" ｜ ")
print()

print("\n===== 事件表结构 =====")
for t in ("events", "chk", "event_scenes"):
    try:
        print(t, [x[1] for x in c.execute(f"pragma table_info({t})")])
    except Exception as e:
        print(t, "无")
