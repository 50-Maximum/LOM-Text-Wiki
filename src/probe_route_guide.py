# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("含 ch5_4_8_9 的事件页:")
for slug, f2 in c.execute("""select slug,facet2 from pages
                             where type='事件' and sections like '%ch5_4_8_9%'"""):
    print("   %-24s %s" % (slug, f2))
print("\n含 S0003_02_01 的事件页:")
for slug, f2 in c.execute("""select slug,facet2 from pages
                             where type='事件' and sections like '%S0003_02_01%' limit 5"""):
    print("   %-24s %s" % (slug, f2))
