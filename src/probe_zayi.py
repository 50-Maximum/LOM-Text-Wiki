# -*- coding: utf-8 -*-
"""查「杂役/打杂」在正式剧情里的用法，决定赵活简介怎么改。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for kw in ("杂役", "打杂"):
    rows = list(c.execute("select script,seq,speaker,text from lines where text like ?", ("%" + kw + "%",)))
    print("=== %s 命中 %d" % (kw, len(rows)))
    for sc, seq, sp, tx in rows[:8]:
        print("  %-16s %4d %-8s %s" % (sc, seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:90]))
