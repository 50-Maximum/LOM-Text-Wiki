# -*- coding: utf-8 -*-
"""看 91 条无正文的 Section 事件：剧本是否存在、是否在库里。"""
import io, json, os, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
rows = json.load(open(os.path.join(BASE, "data", "_map_evt_todo.json"), encoding="utf-8"))
no = [x for x in rows if not x["text"]]
print("无正文", len(no))
print("无剧本的:", sum(1 for x in no if not x["script"]))
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
miss = 0
for x in no[:12]:
    sc = x["script"]
    n = c.execute("select count(*) from lines where script=?", (sc,)).fetchone()[0] if sc else 0
    s = c.execute("select title,line_count from scenes where script=?", (sc,)).fetchone() if sc else None
    print("   %-26s %-30s lines=%d scene=%s" % (x["code"], sc, n, s))
# 剧本文件是否存在
RAW = os.path.join(BASE, "data", "raw")
cnt = 0
for x in no:
    sc = x["script"]
    if not sc:
        continue
    hit = False
    for root, ds, fs in os.walk(RAW):
        if sc + ".txt" in fs or sc in fs:
            hit = True
            break
    if hit:
        cnt += 1
print("\n无正文中，data/raw 里能找到剧本文件的:", cnt, "/", len(no))
