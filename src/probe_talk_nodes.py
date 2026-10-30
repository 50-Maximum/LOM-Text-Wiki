# -*- coding: utf-8 -*-
"""查 talk 菜单场景的选项是否在 branch_nodes 里、文案是什么。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for sc in ["S0208_04_break_start_01", "S0003_03_break_01"]:
    rows = c.execute("select seq,kind,idx,text,cond from branch_nodes where script=? order by seq,idx limit 12",
                     (sc,)).fetchall()
    print("\n==", sc, "节点", len(rows))
    for r in rows:
        print("   %-7s #%s %s" % (r["kind"], r["idx"], (r["text"] or "")[:44]))
