# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("=== section_01_free_07_* ===")
for sc, t in c.execute("select script,title from scenes where script like 'section_01_free_07%' order by script"):
    print("  %-36s %s" % (sc, (t or "")[:30]))
print("\n=== section_01_free_% 全部前缀 ===")
for r in c.execute("""select substr(script,1,22) p, count(*) n from scenes
                      where script like 'section_01_free_%' group by p order by p"""):
    print("  %-26s %d" % (r[0], r[1]))
