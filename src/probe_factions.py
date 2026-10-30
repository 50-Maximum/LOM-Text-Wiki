# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
names = [r[0] for r in c.execute("select name from pages where type='势力' order by mentions desc limit 24")]
print("势力（按提及）:", "、".join(names))
rows = list(c.execute("select coalesce(facet,''), count(*) from pages where type='势力' group by 1 order by 2 desc limit 8"))
print("现有 facet:", rows)
