# -*- coding: utf-8 -*-
"""给占位式势力页取证据：每个词拉 6 条原文。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
terms = ["人间道", "修罗道", "畜生道", "饿鬼道", "地狱道", "天道", "大义分舵", "大仁分舵",
         "忠国公府", "新极乐七仙", "马军司", "夺魄门", "铁拳门", "飞天门", "玄功门"]
for t in terms:
    print("\n###", t)
    rows = c.execute("select script,speaker,text from lines where text like ? limit 6", ("%" + t + "%",)).fetchall()
    for s, sp, tx in rows[:5]:
        print("   [%s] %s：%s" % (s, sp or "旁白", tx.replace("\n", " ")[:80]))
