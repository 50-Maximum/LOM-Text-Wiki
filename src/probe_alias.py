# -*- coding: utf-8 -*-
import sqlite3, io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("===== 人物页里疑似势力的 =====")
for (n,) in c.execute("select name from pages where type='人物' order by name"):
    if any(x in n for x in ("帮", "派", "门", "教", "盟", "会", "家", "阁", "寺", "楼", "庄")):
        print(n, end=" ｜ ")
print()

print("\n===== 人物/飞石帮 的笔记 =====")
for r in c.execute("select script,seq_from,note,quote from notes where type='人物' and name='飞石帮' limit 10"):
    print(r)

print("\n===== 跪求药人 相关场景 =====")
for r in c.execute("select script,title,place,chapter from scenes where title like '%跪求%' or title like '%求药%' limit 10"):
    print(r)
for r in c.execute("select script,seq_from,type,name,note,quote from notes where note like '%求药%' or note like '%跪求%' limit 10"):
    print(r)

print("\n===== 江湖快报 机制 =====")
for r in c.execute("select name,body from guide_events where body like '%江湖快报%' limit 3"):
    print(r[0], r[1][:300])

print("\n===== 魏招弟/魏小菊/魏大才女 原文 =====")
for kw in ("魏招弟", "魏小菊", "魏大才女", "颜师兄", "飞天护法", "飞天掌门"):
    rows = c.execute("select script,seq,speaker from lines where text like ? or speaker like ? limit 4",
                     (f"%{kw}%", f"%{kw}%")).fetchall()
    print(kw, rows)
