# -*- coding: utf-8 -*-
"""等 build_notes 跑完：笔记数连续 3 分钟不变即视为结束。"""
import sqlite3, time, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
last = -1
same = 0
while True:
    try:
        c = sqlite3.connect(DB, timeout=5)
        n, s = c.execute("select count(*), count(distinct script) from notes").fetchone()
        c.close()
    except Exception as e:
        print("读库失败", e, flush=True)
        time.sleep(20)
        continue
    print(f"{time.strftime('%H:%M:%S')} 笔记 {n} 场景 {s}", flush=True)
    if n == last and s >= 1400:
        same += 1
    else:
        same = 0
    if same >= 6:
        print("连续 3 分钟无增长，判定结束", flush=True)
        break
    if s >= 1505:
        print("场景数已达标", flush=True)
        break
    last = n
    time.sleep(30)
