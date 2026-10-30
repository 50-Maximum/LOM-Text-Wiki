# -*- coding: utf-8 -*-
"""复核准备入库的几个势力判定：白猿祖师、象池修士、翼王、火护法、孟仙谣。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for nm in ["白猿祖师", "象池修士", "翼王", "火护法", "孟仙谣", "剑圣", "七星剑主"]:
    print("\n==", nm)
    for r in c.execute("select script,seq,speaker,text from lines where text like ? limit 4", ("%" + nm + "%",)):
        print("   [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:85]))
