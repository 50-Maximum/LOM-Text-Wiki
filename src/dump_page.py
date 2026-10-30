# -*- coding: utf-8 -*-
"""打印页面 JSON，检查结构。用法: python dump_page.py DB SLUG [N]"""
import os, sys, io, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
db = sys.argv[1]
slug = sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
c = sqlite3.connect(db)
row = c.execute("select slug,type,name,lead,infobox,sections,cats,mentions,chapters from pages where slug=?", (slug,)).fetchone()
if not row:
    print("无此页:", slug)
    # 找相近
    for r in c.execute("select slug from pages where slug like ? limit 10", (f"%{slug}%",)):
        print("   ", r[0])
    sys.exit()
print("slug:", row[0], "| type:", row[1], "| name:", row[2])
print("lead:", row[3])
print("infobox:", row[4])
print("cats:", row[6], "mentions:", row[7], "chapters:", row[8])
secs = json.loads(row[5])
print("sections:", len(secs))
txt = json.dumps(secs, ensure_ascii=False, indent=1)
print(txt[:n])
print("\nlinks:")
for r in c.execute("select dst,kind,label from links where src=? limit 25", (slug,)):
    print("   ", r)
