# -*- coding: utf-8 -*-
"""按类型各抽一页，检查导语与首段是否合理。"""
import io, sys, sqlite3, json, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
random.seed(11)
types = [r[0] for r in c.execute("select distinct type from pages")]
for t in sorted(types):
    rows = c.execute("select slug,name,lead from pages where type=? order by random() limit 1", (t,)).fetchall()
    if not rows:
        continue
    slug, nm, lead = rows[0]
    print("%-6s %-26s %s" % (t, nm[:24], (lead or "")[:70]))
