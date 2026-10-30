# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
rows = c.execute("""select name, slug, (select count(*) from links where dst=pages.slug) as n
                    from pages where type='人物' order by n desc""").fetchall()
print("人物页", len(rows))
out = []
for nm, slug, n in rows:
    out.append("%-16s %4d" % (nm, n))
for i in range(0, len(out), 6):
    print("  ".join(out[i:i + 6]))
