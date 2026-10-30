# -*- coding: utf-8 -*-
"""逐场核对：把结果写成 UTF-8 文件 data/_show.txt，供人工/只读工具查看。
用法：python show_scene.py ch4_4_1 ch4_1_3 ...
"""
import io, os, sqlite3, sys

OUT = r"D:\LegendOfMortal Wiki\data\_show.txt"
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row
PL = [r["name"] for r in con.execute("select name from pages where type='地点'")]
KEY = sorted({p.split("-")[-1] for p in PL} | {"唐门", "崆峒", "青城", "江陵", "襄阳",
                                              "峨嵋", "点苍", "眉山", "大理", "汴京", "临安"},
             key=len, reverse=True)

buf = []
for sc in sys.argv[1:]:
    d = con.execute("select script,title,chapter,place,cjk from scenes where script=?", (sc,)).fetchone()
    if not d:
        buf.append("缺场景 %s" % sc)
        continue
    buf.append("=" * 72)
    buf.append("%s | %s | %s | 现标：%s | %d 字" % (d["script"], d["title"], d["chapter"],
                                                d["place"], d["cjk"]))
    rows = list(con.execute("select seq, speaker, text from lines where script=? order by seq", (sc,)))
    buf.append("--- 开场 ---")
    for r in rows[:6]:
        buf.append("  #%d %s %s" % (r["seq"], (r["speaker"] or "")[:8], (r["text"] or "")[:120]))
    buf.append("--- 含地名句（最多 10 条）---")
    n = 0
    for r in rows:
        t = r["text"] or ""
        hit = [k for k in KEY if k in t]
        if hit:
            buf.append("  #%d %s [%s] %s" % (r["seq"], (r["speaker"] or "")[:8],
                                             "/".join(hit[:3]), t[:120]))
            n += 1
            if n >= 10:
                break
open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("written", OUT, len(buf), "lines")
