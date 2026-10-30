# -*- coding: utf-8 -*-
"""列出「夺魄」当作地点的场景，附开场与关键词，供细判驻地。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
OV = json.load(open(os.path.join(BASE, "data", "place_override.json"), encoding="utf-8"))
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row
rows = list(c.execute("select script,title,chapter,cjk from scenes where place='夺魄' order by script"))
buf = []
todo = []
for r in rows:
    if r["script"] in OV:
        continue
    lines = list(c.execute("select seq,speaker,text from lines where script=? order by seq",
                           (r["script"],)))[:8]
    buf.append("%s｜%s｜%s｜%d 字" % (r["script"], r["title"], r["chapter"], r["cjk"]))
    for l in lines[:4]:
        buf.append("   #%d %s %s" % (l["seq"], (l["speaker"] or "")[:8], (l["text"] or "")[:100]))
    buf.append("")
    todo.append(r["script"])
open(os.path.join(BASE, "data", "_duopo.txt"), "w", encoding="utf-8").write("\n".join(buf))
print("夺魄场次合计 %d，待判 %d" % (len(rows), len(todo)))
print(",".join(todo))
