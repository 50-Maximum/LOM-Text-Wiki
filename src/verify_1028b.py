# -*- coding: utf-8 -*-
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("== 华山派 相关页 ==")
for r in c.execute("select type,name from pages where name like '%华山派%'"):
    print("   %-6s %s" % (r["type"], r["name"]))
print("\n== 四人主角页 ==")
for nm in ["丐帮·王二壮", "铁拳门·雷谦", "飞天门·火龙仙君", "市井·吕翁", "丐帮·毛二壮"]:
    r = c.execute("select name,title,substr(lead,1,50) as ld,facet from pages where type='人物' and name=?", (nm,)).fetchone()
    if r:
        print("   %-16s 称号=%-8s 筛=%s | %s" % (r["name"], r["title"] or "-", r["facet"], r["ld"]))
    else:
        print("   %-16s 无页" % nm)
print("\n== 势力页数 ==", c.execute("select count(*) from pages where type='势力'").fetchone()[0])
print("== 人物页数 ==", c.execute("select count(*) from pages where type='人物'").fetchone()[0])
