# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
n = c.execute("select count(*) from pages where sections like '%出自梦境%'").fetchone()[0]
print("页面里带「出自梦境」标注的：%d 个" % n)
for slug, in c.execute("select slug from pages where sections like '%出自梦境%' limit 6"):
    print("  " + slug)
print("\n带「梦境提示」的页面：%d" % c.execute(
    "select count(*) from pages where sections like '%梦境提示%'").fetchone()[0])
