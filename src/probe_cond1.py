# -*- coding: utf-8 -*-
import sqlite3, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for t in ("guide_events", "guide_index", "scene_time"):
    print("==", t, "==")
    cols = [r[1] for r in c.execute(f"PRAGMA table_info({t})")]
    print(" cols:", cols)
    print(" rows:", c.execute(f"select count(*) from {t}").fetchone()[0])
    for r in c.execute(f"select * from {t} limit 2"):
        print("  ", [str(x)[:110] for x in r])
print("\n== branch cond 样例 ==")
for r in c.execute("select script,seq,kind,text,cond,flags from branch_nodes where cond is not null and cond<>'' limit 12"):
    print("  ", [str(x)[:90] for x in r])
print("\n== branch kind 分布 ==")
for r in c.execute("select kind,count(*) from branch_nodes group by kind order by 2 desc"):
    print("  ", r)
