# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
for sc in ("ch7_5_2_2", "ch7_6_1", "ch6_9_2", "ch6_9_2_3", "ch6_9_2_4", "ch8_5_1", "ch8_8_1"):
    n = c.execute("select count(*) from lines where script=?", (sc,)).fetchone()[0]
    print(sc, n, "句")

print("\n===== 魏菊 笔记（ch7 附近） =====")
for r in c.execute("""select script,seq_from,name,note,quote from notes
                      where name like '%魏菊%' and script like 'ch7%' limit 15"""):
    print(f"{r[0]}#{r[1]} [{r[2]}] {r[3][:50]} | {r[4][:30]}")

print("\n===== 孟仙谣 笔记 =====")
for r in c.execute("""select script,seq_from,name,note,quote from notes
                      where (name like '%孟仙谣%' or note like '%孟仙谣%') limit 20"""):
    print(f"{r[0]}#{r[1]} [{r[2]}] {r[3][:50]} | {r[4][:30]}")
