# -*- coding: utf-8 -*-
"""核验：腾云寨已无页、地点页出现「发生场景」、redirect 可用。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

print("腾云寨 页面:", [r["slug"] for r in c.execute(
    "select slug from pages where name='腾云寨'")] or "已删除")
print("腾云山 页面:", [r["slug"] for r in c.execute(
    "select slug from pages where name='腾云山'")] or "缺失")
print("重定向 腾云寨→:", [tuple(r) for r in c.execute(
    "select src,dst from redirects where src like '%腾云寨%'")])

for slug in ("地点/崆峒-铁拳巷", "地点/江陵", "地点/唐门"):
    r = c.execute("select sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        print(slug, "缺页")
        continue
    hs = [(s.get("h"), len(s.get("rows") or [])) for s in json.loads(r["sections"] or "[]")]
    print("%-18s %s" % (slug, hs))
