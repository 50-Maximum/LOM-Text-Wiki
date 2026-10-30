# -*- coding: utf-8 -*-
"""最终核验：转场提示、路由传参、区域页隐藏、顶层地点的筛选合计。"""
import io, json, re, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

h = open(r"D:\LegendOfMortal Wiki\web\wiki.html", encoding="utf-8").read()
print("A 路由把 ?seq 传给 renderScene:", "renderScene(arg + (_q ? ('?' + _q) : ''))" in h)

c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
r = c.execute("select lead from pages where slug='场景/S2321_02_01'").fetchone()
print("B S2321_02_01 导语:", (r["lead"][:80] if r else "无页面"))
print("C 地点/川蜀 hidden:", c.execute(
    "select hidden from pages where slug='地点/川蜀'").fetchone()["hidden"])
print("D 巴渝 残留:", c.execute(
    "select count(*) from pages where type='地点' and facet='巴渝'").fetchone()[0])
top = c.execute("""select count(*) from pages where type='地点' and hidden=0
                   and slug not in (select slug from place_children)""").fetchone()[0]
s = c.execute("""select sum(n) from (select facet, count(*) n from pages where type='地点'
                 and hidden=0 and slug not in (select slug from place_children)
                 group by facet)""").fetchone()[0]
print("E 顶层地点 %d，区域档求和 %d" % (top, s))
print("F 新增/改名抽查:", [(x["slug"], x["hidden"]) for x in c.execute(
    "select slug,hidden from pages where name in ('崆峒山村','唐门-谷底','豆浆店','鬼岛','南沟集')")])
