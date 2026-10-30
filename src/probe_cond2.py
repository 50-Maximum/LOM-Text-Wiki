# -*- coding: utf-8 -*-
import sqlite3, io, sys, re, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
db = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(db).cursor()
print("guide_events cond 非空:", c.execute("select count(*) from guide_events where cond is not null and trim(cond)<>''").fetchone()[0], "/71")
print("guide_index body 含触发:", c.execute("select count(*) from guide_index where body like '%触发%'").fetchone()[0], "/150")
print("guide_index body 含条件:", c.execute("select count(*) from guide_index where body like '%条件%'").fetchone()[0])
print("guide_index body 含概率:", c.execute("select count(*) from guide_index where body like '%概率%'").fetchone()[0])
print("\n-- 触发样例 --")
for (nm, b) in c.execute("select name,body from guide_index where body like '%触发%' limit 6"):
    m = re.findall(r".{0,40}触发.{0,60}", b)
    print(" ", nm, "|", m[:2])
print("\n-- 条件样例 --")
for (nm, b) in c.execute("select name,body from guide_index where body like '%条件%' limit 6"):
    m = re.findall(r".{0,30}条件.{0,70}", b)
    print(" ", nm, "|", m[:2])

# 原始脚本里找场景跳转与条件
raw = r"D:\LegendOfMortal Wiki\data\raw"
fs = glob.glob(os.path.join(raw, "*.txt"))
print("\nraw 文件数:", len(fs))
sample = os.path.join(raw, "ch5_4_7_2_1.txt")
if os.path.exists(sample):
    t = open(sample, encoding="utf-8", errors="replace").read()
    print("\n-- 对白/条件格式样例 ch5_4_7_2_1 前 60 行 --")
    for ln in t.splitlines()[:60]:
        print("   ", ln[:150])
