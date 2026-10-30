# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("== 各阶段事件数 ==")
rows = c.execute("select facet,count(*) n from pages where type='事件' group by facet order by n desc").fetchall()
for r in rows:
    print("   %-12s %d" % (r["facet"] or "(空)", r["n"]))
print("\n== 抽查 ==")
for kw in ["段考约战", "江陵事变", "万里鹏程挑战赵活", "三人道中遇敌拦路",
           "外姓弟子月度评鉴", "唐门商议应对飞石帮", "郁竹答应求婚"]:
    r = c.execute("select name,facet,infobox from pages where type='事件' and name like ?", ("%" + kw + "%",)).fetchone()
    if r:
        inf = json.loads(r["infobox"] or "{}")
        print("   %-26s 阶段=%-10s 出现=%s" % (r["name"], r["facet"], inf.get("出现阶段", "-")))
    else:
        print("   %-26s 无页" % kw)
