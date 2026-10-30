# -*- coding: utf-8 -*-
"""查 O_xxx 选项键的中文出处。"""
import os, sys, io, sqlite3, re, json, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))

print("== choices 表结构 ==")
for r in c.execute("PRAGMA table_info(choices)"):
    print("  ", r)
print("== 样本 ==")
for r in c.execute("select * from choices limit 8"):
    print("  ", r)

print("\n== kv 表里有没有 O_ ===")
try:
    for r in c.execute("select k,v from kv where k like 'O\\_%' escape '\\' limit 5"):
        print("  ", r)
except Exception as e:
    print("  kv 异常", e)
try:
    n = c.execute("select count(*) from kv where k like 'O\\_%' escape '\\'").fetchone()[0]
    print("  共", n)
except Exception as e:
    print(e)

print("\n== text.json 里有没有 O_ ===")
tf = os.path.join(BASE, "data", "build", "text.json")
t = json.load(open(tf, encoding="utf-8"))
print("  keys:", len(t))
hit = [k for k in t if k.startswith("O_")]
print("  O_ 开头:", len(hit), hit[:5])
# 招亲场景的选项键
rows = c.execute("select script, idx, key, text from choices where script like '%5_3%' limit 20").fetchall()
print("\n== 招亲相关 choices ==")
for r in rows:
    print("  ", r)
