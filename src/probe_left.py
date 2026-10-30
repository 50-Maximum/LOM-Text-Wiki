# -*- coding: utf-8 -*-
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("== 史实 残留 ==")
for r in c.execute("select name from pages where type='人物' and name like '史实·%'"):
    print("   ", r["name"])
print("== 杏花林 ==")
for r in c.execute("select name from pages where name like '%杏花林%'"):
    print("   ", r["type"] if "type" in r.keys() else "", r["name"])
print("== 江湖 剩余（前 60） ==")
for r in c.execute("select name from pages where type='人物' and name like '江湖·%' order by name"):
    print("   ", r["name"])
