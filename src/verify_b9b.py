# -*- coding: utf-8 -*-
"""核验：腾云寨已删、重定向存在、地点页出现「发生场景」。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

print("redirects 列:", [r[1] for r in c.execute("pragma table_info(redirects)")])
cols = [r[1] for r in c.execute("pragma table_info(redirects)")]
rows = c.execute("select * from redirects where %s like ?" % cols[0], ("%腾云寨%",)).fetchall()
print("腾云寨 重定向:", [tuple(r) for r in rows] or "无")

for slug in ("地点/崆峒-铁拳巷", "地点/江陵", "地点/唐门", "地点/腾云山"):
    r = c.execute("select sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        print("%-18s 缺页" % slug)
        continue
    hs = [(s.get("h"), len(s.get("rows") or [])) for s in json.loads(r["sections"] or "[]")]
    print("%-18s %s" % (slug, hs))
