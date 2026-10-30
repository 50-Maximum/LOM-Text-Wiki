# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("entries 字段:", [r[1] for r in c.execute("pragma table_info(entries)")])
for r in c.execute("select ns,count(*) from entries group by 1 order by 2 desc limit 12"):
    print("   ", r)
try:
    for r in c.execute("select * from entries where ns='ItemBook_zh-cn' limit 2"):
        print("   样例:", str(r)[:220])
except Exception as e:
    print(e)
