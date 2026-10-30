# -*- coding: utf-8 -*-
"""用攻略索引建立 场景脚本 → 游戏时间（年/月/旬/事件）映射，并按时间划分七个阶段。"""
import sqlite3, io, sys, re, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)

rows = c.execute("select year,month,xun,name,scripts,sec from guide_index").fetchall()
m = {}
for y, mo, x, name, scripts, sec in rows:
    if not y or not mo:
        continue
    for sc in (scripts or "").split(","):
        sc = sc.strip()
        if not sc:
            continue
        # 过滤掉把选项文字粘进来的脏值
        if "选项" in sc or "：" in sc or len(sc) > 60:
            continue
        m.setdefault(sc, (y, mo, x or "", name, sec or ""))

# 也收 guide_events 里带脚本的（body 内 游戏脚本）
for name, body in c.execute("select name,body from guide_events"):
    pass

print("映射脚本数", len(m))
c.execute("drop table if exists scene_time")
c.execute("create table scene_time(script text primary key, year int, month int, xun text, event text, sec text)")
c.executemany("insert or replace into scene_time values(?,?,?,?,?,?)",
              [(k, v[0], v[1], v[2], v[3], v[4]) for k, v in m.items()])
c.commit()

# 阶段划分（按时间）
def arc_of_time(y, mo):
    if not y or not mo:
        return ""
    if (y, mo) <= (1, 11):
        return "外姓弟子"
    if (y, mo) <= (2, 8):
        return "南宫寿宴"
    if (y, mo) <= (2, 10):
        return "江陵围城"
    if (y, mo) <= (3, 4):
        return "唐门衰败"
    if (y, mo) <= (3, 7):
        return "比武招亲"
    if (y, mo) <= (3, 11):
        return "武林大会"
    return "武林盟进攻唐门"

dist = {}
for sc, (y, mo, x, name, sec) in m.items():
    a = arc_of_time(y, mo)
    dist[a] = dist.get(a, 0) + 1
print("按时间落到阶段的脚本：", dist)

# 抽样核对
print("\n抽样：")
for sc in ("ch1_1_2", "ch2_2_1", "ch2_5_1", "ch3_2_1", "ch5_3_1", "S9001_01", "ch8_5_1"):
    r = c.execute("select year,month,xun,event from scene_time where script=?", (sc,)).fetchone()
    print(sc, r)
