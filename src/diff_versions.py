# -*- coding: utf-8 -*-
"""新旧版本对比：场景/台词增量、新增与消失脚本、关键新内容是否入库。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
NEW = r"D:\LegendOfMortal Wiki\data\wiki.db"
OLD = r"D:\LegendOfMortal Wiki\data\wiki.db.bak_before_6001"
n = sqlite3.connect(NEW)
o = sqlite3.connect(OLD)
n.row_factory = sqlite3.Row

print("场景 %d → %d ／ 台词 %d → %d ／ 条目 %d" % (
    o.execute("select count(*) from scenes").fetchone()[0],
    n.execute("select count(*) from scenes").fetchone()[0],
    o.execute("select count(*) from lines").fetchone()[0],
    n.execute("select count(*) from lines").fetchone()[0],
    n.execute("select count(*) from pages").fetchone()[0]))

os_ = {r[0] for r in o.execute("select script from scenes")}
ns_ = {r[0] for r in n.execute("select script from scenes")}
print("\n新增场景:", sorted(ns_ - os_))
print("消失场景:", sorted(os_ - ns_))

added = []
for r in n.execute("select script,count(*) c from lines group by script"):
    old_c = o.execute("select count(*) from lines where script=?", (r["script"],)).fetchone()[0]
    if r["c"] != old_c:
        added.append((r["c"] - old_c, r["script"], old_c, r["c"]))
added.sort(reverse=True)
print("\n台词数变化最多的 12 个场景（差/脚本/旧/新）:")
for x in added[:12]:
    print("   %+4d %-24s %d → %d" % x)

for kw in ["思想战", "唐门暗器总纲", "回想"]:
    c = n.execute("select count(*) from lines where text like ?", ("%" + kw + "%",)).fetchone()[0]
    print("\n关键词「%s」命中 %d 句" % (kw, c))
    for r in n.execute("select script,seq,substr(text,1,70) t from lines where text like ? limit 3",
                       ("%" + kw + "%",)):
        print("   %s#%s %s" % (r["script"], r["seq"], r["t"].replace("\n", " ")))
