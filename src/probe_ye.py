# -*- coding: utf-8 -*-
"""读叶云裳救治相关的条件文本，确认「谁救她」的分支。"""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

for sc in ("S0204_01_04_02", "S0204_01_04_break_start_01", "S0208_05_05"):
    rows = c.execute("select seq,speaker,text from lines where script=? order by seq", (sc,)).fetchall()
    print(f"\n===== {sc}（{len(rows)} 句）=====")
    hit = [i for i, (q, sp, tx) in enumerate(rows) if tx and ("梁有诗" in tx or "出窍针" in tx or "郁竹" in tx or "救" in tx)]
    shown = set()
    for i in hit[:8]:
        for j in range(max(0, i - 2), min(len(rows), i + 3)):
            if j in shown:
                continue
            shown.add(j)
            q, sp, tx = rows[j]
            print(f"  #{q} {sp}：{(tx or '').replace(chr(10),' ')[:90]}")

print()
print("== notes 样例 ==")
for r in c.execute("select script,seq_from,type,name,note,quote from notes order by rowid desc limit 6"):
    print("  ", r)
