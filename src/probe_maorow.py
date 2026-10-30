# -*- coding: utf-8 -*-
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
cols = [d[1] for d in c.execute("pragma table_info(pages)")]
print("列:", cols)
for r in c.execute("select * from pages where name like '%毛二壮%' or name like '崆峒·%'"):
    print({k: (str(r[k])[:40] if isinstance(r[k], str) else r[k]) for k in cols})
