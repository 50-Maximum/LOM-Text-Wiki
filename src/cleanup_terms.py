# -*- coding: utf-8 -*-
import sqlite3, re

c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.execute("PRAGMA journal_mode=WAL")

NOISE_FAC = ("不会", "一定", "可能", "当然", "迟早", "绝不", "就该", "也就", "各门各派",
             "六大派", "武林大会", "掌派", "指教", "请你", "敢问", "先过", "随我",
             "杀上", "开门", "时梦", "见从")
for w in NOISE_FAC:
    c.execute("DELETE FROM factions WHERE name LIKE ?", ("%" + w + "%",))

NOISE_TERM = ("你", "我", "他", "她", "请", "敢", "先", "随", "杀", "开", "时梦",
              "见从", "不会", "一定", "可能", "当然", "迟早", "绝不", "各门各派",
              "六大派", "掌派", "指教", "进来", "出来", "回来", "起来", "上去", "下去")
for w in NOISE_TERM:
    c.execute("DELETE FROM terms WHERE name LIKE ?", ("%" + w + "%",))
c.commit()

print("factions", c.execute("SELECT COUNT(*) FROM factions").fetchone()[0])
print("terms", c.execute("SELECT COUNT(*) FROM terms").fetchone()[0])
for r in c.execute("SELECT type,COUNT(*) n FROM terms GROUP BY type"):
    print(" ", r[0], r[1])
for r in c.execute("SELECT name FROM factions WHERE name LIKE '%千灯%' OR name LIKE '%火炎%' OR name LIKE '%上官%'"):
    print(" faction:", r[0])
