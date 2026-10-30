# -*- coding: utf-8 -*-
"""上官萤「东瀛北条家提亲」是否有原文；顺带看她的婚事相关句。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("=== 北条")
for sc, seq, sp, tx in c.execute("""select script,seq,speaker,text from lines
    where text like '%北条%' order by script,seq limit 10"""):
    print("  %-24s %-4s %-8s %s" % (sc, seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:76]))
print("\n=== 上官萤 + 嫁/提亲/成亲")
for sc, seq, sp, tx in c.execute("""select script,seq,speaker,text from lines
    where text like '%上官萤%' and (text like '%嫁%' or text like '%提亲%' or text like '%成亲%')
    order by script,seq limit 10"""):
    print("  %-24s %-4s %-8s %s" % (sc, seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:76]))
