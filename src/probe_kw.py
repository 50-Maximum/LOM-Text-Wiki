# -*- coding: utf-8 -*-
import sqlite3, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
kws = ["邹博", "掌派", "金乌上人", "南宫深", "代掌门", "租客", "梁有诗", "小医仙", "音信"]
os.makedirs(r"D:\LegendOfMortal Wiki\data\probe", exist_ok=True)
out = []
for kw in kws:
    rows = c.execute("""select script,seq_from,name,note,quote from notes
                        where name like ? or note like ? order by script,seq_from""",
                     (f"%{kw}%", f"%{kw}%")).fetchall()
    out.append(f"===== {kw} ({len(rows)}) =====")
    for r in rows:
        out.append(f"{r[0]}#{r[1]} [{r[2]}] {r[3][:70]} | {r[4][:40]}")
open(r"D:\LegendOfMortal Wiki\data\probe\kw.txt", "w", encoding="utf-8").write("\n".join(out))
print("done, lines:", len(out))
