# -*- coding: utf-8 -*-
"""把全文按章切成分批阅读文件，并统计规模。"""
import sqlite3, os, collections

DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
OUT = r"D:\LegendOfMortal Wiki\data\read"
os.makedirs(OUT, exist_ok=True)
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row

by_ch = collections.defaultdict(list)
for r in c.execute("""SELECT s.chapter, l.script, l.seq, l.speaker, l.text
                      FROM lines l JOIN scenes s ON s.script=l.script
                      ORDER BY s.chapter, l.script, l.seq"""):
    by_ch[r["chapter"]].append((r["script"], r["seq"], r["speaker"], r["text"] or ""))

total = 0
for ch, rows in by_ch.items():
    fn = os.path.join(OUT, ch.replace("/", "_") + ".txt")
    with open(fn, "w", encoding="utf-8") as f:
        cur = ""
        for sc, seq, sp, tx in rows:
            if sc != cur:
                f.write("\n===== %s =====\n" % sc)
                cur = sc
            f.write("[%d] %s：%s\n" % (seq, sp, tx))
    size = os.path.getsize(fn)
    total += size
    print("%-6s %6d 句  %7.1f KB" % (ch, len(rows), size / 1024))
print("总大小 %.1f MB" % (total / 1048576))
