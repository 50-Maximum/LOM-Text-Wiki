# -*- coding: utf-8 -*-
"""重建后复查：事件发生地覆盖率、推断标记、规范名是否统一。"""
import io, sys, json, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

n = c.execute("select count(*) from pages where type='事件'").fetchone()[0]
n0 = c.execute("""select count(*) from pages where type='事件'
                  and (json_extract(infobox,'$.发生地') is null
                       or json_extract(infobox,'$.发生地')='')""").fetchone()[0]
ni = c.execute("""select count(*) from pages where type='事件'
                  and json_extract(infobox,'$.发生地') like '%（推断）%'""").fetchone()[0]
print("事件 %d ｜ 无地点 %d ｜ 推断 %d" % (n, n0, ni))

print("\n=== 事件发生地分布（前 12）")
for p, k in c.execute("""select json_extract(infobox,'$.发生地') p, count(*) from pages
                         where type='事件' group by p order by 2 desc limit 12"""):
    print("  %-22s %d" % (p, k))

print("\n=== 还有没有短名地点（夺魄/崆峒/青城 单独出现）")
for pat in ("夺魄", "崆峒", "青城"):
    k = c.execute("""select count(*) from pages where type='事件'
                     and json_extract(infobox,'$.发生地') = ?""", (pat,)).fetchone()[0]
    print("  %s: %d" % (pat, k))

print("\n=== 抽样：推断出来的事件")
for slug, inf in c.execute("""select slug,json_extract(infobox,'$.发生地') from pages
                              where type='事件' and json_extract(infobox,'$.发生地') like '%推断%'
                              limit 6"""):
    print("  ", slug, "→", inf)
