# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("===== notes type 分布 =====")
for r in c.execute("select type,count(*) from notes group by type order by 2 desc limit 12"):
    print(r)

print("\n===== 唐芳赠丹 notes =====")
for r in c.execute("select script,seq_from,name,note,quote from notes where note like '%唐芳赠丹%' or note like '%赠丹%' limit 10"):
    print(f"{r[0]}#{r[1]} [{r[2]}] {r[3][:55]} | {r[4][:34]}")

print("\n===== 四门 line =====")
for r in c.execute("select script,seq,speaker,replace(substr(text,1,80),char(10),'/') from lines where text like '%飞天门%' and text like '%夺魄门%' limit 8"):
    print(f"{r[0]}#{r[1]} [{r[2]}] {r[3]}")

print("\n===== 金乌/火龙仙君 掌门身份 line =====")
for r in c.execute("select script,seq,speaker,replace(substr(text,1,80),char(10),'/') from lines where text like '%金乌上人%' and text like '%火龙仙君%' and text like '%掌门%' limit 8"):
    print(f"{r[0]}#{r[1]} [{r[2]}] {r[3]}")

print("\n===== ch8_1_1_2_2_1 条件（branch_nodes 或 parent） =====")
for r in c.execute("select * from branch_nodes where script='ch8_1_1_2_2_1' limit 8"):
    print(r)
