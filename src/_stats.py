# -*- coding: utf-8 -*-
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
print("== pages by type ==")
for t, n in c.execute("select type, count(*) from pages group by type order by count(*) desc"):
    print("%-12s %6d" % (t, n))
print("== 台词 ==")
print("lines", c.execute("select count(*) from lines").fetchone()[0])
print("speakers", c.execute("select count(distinct speaker) from lines where speaker is not null and speaker<>''").fetchone()[0])
cjk = c.execute("select sum(length(text)) from lines").fetchone()[0]
print("字数", cjk)
print("== 场景/分支 ==")
for q, label in [("select count(*) from scenes", "scenes"),
                 ("select count(*) from choices", "choices"),
                 ("select count(*) from branch_nodes", "branch_nodes"),
                 ("select count(*) from flags", "flag changes"),
                 ("select count(*) from cond", "cond"),
                 ("select count(*) from notes", "notes"),
                 ("select count(*) from guide_events", "guide_events"),
                 ("select count(*) from ledger", "ledger"),
                 ("select count(*) from endings", "endings"),
                 ("select count(*) from links", "links"),
                 ("select count(*) from entities", "entities")]:
    print("%-14s %7d" % (label, c.execute(q).fetchone()[0]))
