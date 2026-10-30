# -*- coding: utf-8 -*-
import sqlite3, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("===== 漏算账目 相关页面 =====")
for r in c.execute("select slug,type,name,lead,mentions from pages where name like '%漏算账目%'"):
    print(r)

print("\n===== 漏算账目 相关笔记 =====")
for r in c.execute("select script,seq_from,seq_to,name,type,substr(note,1,60) from notes where name like '%漏算账目%' limit 10"):
    print(r)

print("\n===== 含'夜咳'的lines =====")
for r in c.execute("select script,seq,speaker,replace(substr(text,1,70),char(10),'/') from lines where text like '%夜咳%' or text like '%漏算%' limit 10"):
    print(r)
