# -*- coding: utf-8 -*-
"""查这几个词在原文里的实际用法，决定页面名与上级。"""
import io, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row
for w in ["讲经堂", "讲经楼", "大铁铺", "半雨屏", "无色广场", "赌坊", "老虎山", "田寨村", "镇魂狱"]:
    rows = con.execute("select script,seq,text from lines where text like ? limit 4",
                       ("%" + w + "%",)).fetchall()
    n = con.execute("select count(*) from lines where text like ?", ("%" + w + "%",)).fetchone()[0]
    print("\n=== %s  命中 %d 句" % (w, n))
    for r in rows:
        print("   %s#%s %s" % (r["script"], r["seq"], (r["text"] or "").replace("\n", " ")[:80]))
