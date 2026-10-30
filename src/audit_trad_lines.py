# -*- coding: utf-8 -*-
"""正文繁体残留定位：按 lines 表统计，并看出现在哪些剧本。"""
import io, sys, sqlite3
from opencc import OpenCC
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
CC = OpenCC("t2s")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

tot = 0
bad = []
for sid, sc, seq, tx in c.execute("select id,script,seq,text from lines"):
    if tx and CC.convert(tx) != tx:
        tot += 1
        if len(bad) < 12:
            bad.append((sc, seq, tx))
n_all = c.execute("select count(*) from lines").fetchone()[0]
print("台词含繁体 %d / %d 句" % (tot, n_all))
for sc, seq, tx in bad:
    print("   %-26s %-4s %s" % (sc, seq, tx.replace("\n", " ")[:60]))
