# -*- coding: utf-8 -*-
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\raw\system\Flag_zh-cn.txt"
raw = open(p, "rb").read()
print("前 40 字节:", raw[:40])
txt = raw.decode("utf-8", errors="replace")
lines = txt.splitlines()
print("行数:", len(lines))
for ln in lines[:6]:
    print(repr(ln))
m = {}
for ln in lines:
    mm = re.match(r"Flag/Name/(\w+)\s*=\s*(.+)", ln.strip())
    if mm:
        m[mm.group(1)] = mm.group(2).strip()
print("解析到旗标:", len(m), list(m.items())[:3])
# 事件名对照
import sqlite3
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("\n事件名样例:", [r[0] for r in c.execute("select distinct name from notes where type='事件' limit 20")])
print("\n攻略事件名:", [r[0] for r in c.execute("select name from guide_index limit 12")])
print("\n攻略主线事件:", [r[0] for r in c.execute("select name from guide_events limit 12")])
