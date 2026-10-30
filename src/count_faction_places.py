# -*- coding: utf-8 -*-
"""统计：有多少场景的「地点」其实是势力名（飞石帮、南宫世家…）。"""
import io, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row
fac = {r["name"]: r["slug"] for r in con.execute("select name, slug from pages where type='势力'")}
cnt = collections.Counter()
for r in con.execute("select place, count(*) n from scenes where place<>'' group by place"):
    if r["place"] in fac:
        cnt[r["place"]] = r["n"]
total = sum(cnt.values())
print("场景地点填成势力名的：%d 个势力 / %d 场" % (len(cnt), total))
for k, v in cnt.most_common(15):
    print("   %-8s %d" % (k, v))
