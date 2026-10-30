# -*- coding: utf-8 -*-
"""看铁冠道人 / 不平道长 / 尹道长 是否与「看诗集」有关；并查尹道长页。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for nm in ["铁冠道人", "不平道长", "尹道长", "高和子", "清虚子"]:
    r = c.execute("select name from pages where type='人物' and name like ?", ("%" + nm,)).fetchone()
    print("\n== %-6s 页: %s" % (nm, r["name"] if r else "无"))
    for x in c.execute("select script,seq,speaker,text from lines where text like ? and (text like '%诗%' or text like '%集%' or text like '%书%') limit 3",
                       ("%" + nm + "%",)):
        print("   [%s#%d] %s：%s" % (x["script"], x["seq"], x["speaker"] or "-", (x["text"] or "")[:80]))
