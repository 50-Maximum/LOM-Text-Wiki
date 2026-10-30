# -*- coding: utf-8 -*-
"""最终核验：百万赵活/裴红腊导语、江湖前缀剩余数量。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for nm in ["梦境·百万赵活", "青城派·裴红腊", "丐帮·王二壮"]:
    r = c.execute("select name,lead from pages where type='人物' and name=?", (nm,)).fetchone()
    print("%-12s %s" % (nm, (r["lead"] or "")[:80] if r else "无页"))
rows = [r["name"] for r in c.execute("select name from pages where type='人物' and name like '江湖·%'")]
print("\n江湖前缀剩余", len(rows), "个")
print("、".join(rows[:40]))
