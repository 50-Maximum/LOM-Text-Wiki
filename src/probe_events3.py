# -*- coding: utf-8 -*-
import sqlite3, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("===== 眉山 相关页 =====")
for r in c.execute("select slug,type,name,mentions from pages where name like '%眉山%'"):
    print(r)

print("\n===== 全部地点页（按提及排序，前 60） =====")
kids = {r[0] for r in c.execute("select slug from place_children")}
for r in c.execute("""select slug,json_extract(infobox,'$.上级'),mentions from pages
                      where type='地点' order by mentions desc limit 60"""):
    print(("子" if r[0] in kids else "顶"), r[0], "上级=" + str(r[1]), r[2])

print("\n===== chk 结构 =====")
print([x[1] for x in c.execute("pragma table_info(chk)")])
for r in c.execute("select * from chk limit 3"):
    print(r)

print("\n===== branch_nodes 结构 =====")
print([x[1] for x in c.execute("pragma table_info(branch_nodes)")])
for r in c.execute("select script,seq,kind,idx,text,scenes from branch_nodes where scenes!='[]' limit 5"):
    print(r)

print("\n===== 眉山 唐门 原文 =====")
for r in c.execute("select script,seq,speaker,replace(substr(text,1,80),char(10),'/') from lines where text like '%眉山%' and text like '%唐门%' limit 10"):
    print(r)
