# -*- coding: utf-8 -*-
"""把待重写简介的 39 人，各取最多 10 句原文，导出到 data\\_intro_src.txt。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
todo = json.load(open(os.path.join(B, "research", "intro_todo.json"), encoding="utf-8"))
names = [n for n, _ in todo["bad"]] + [n for n, _ in todo["short"]]
out = []
for disp in names:
    nm = disp.split("·")[-1]
    rows = list(c.execute(
        "select script,seq,speaker,text from lines where text like ? or speaker=? "
        "order by script,seq limit 10", ("%" + nm + "%", nm)))
    out.append("\n===== %s（%d 句） =====" % (disp, len(rows)))
    for r in rows:
        t = (r["text"] or "").replace("\n", "／")
        out.append("[%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", t[:110]))
open(os.path.join(B, "_intro_src.txt"), "w", encoding="utf-8").write("\n".join(out))
print("导出", len(names), "人，", len("\n".join(out)), "字")
