# -*- coding: utf-8 -*-
"""重建后核验：南沟并页、金乌势力删除、谷底归属、区域档。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

print("pages 总数:", c.execute("select count(*) from pages").fetchone()[0])
print("A 南沟:", [(r["slug"], r["hidden"], len(json.loads(r["sections"] or "[]")))
                for r in c.execute("select slug,hidden,sections from pages where name like '南沟%'")])
print("B 金乌势力:", [r["slug"] for r in c.execute(
    "select slug from pages where type='势力' and name='金乌'")] or "已删除")
print("C 谷底页:", [r["slug"] for r in c.execute("select slug from pages where name='唐门-谷底'")])
for sc in ("S0208_03", "S0208_04_02_03", "S0208_05_01"):
    r = c.execute("select sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    txt = ""
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息" and s.get("html"):
            txt = s["html"]
    print("   %-16s %s" % (sc, txt[:70]))
print("D 区域档:")
for r in c.execute("""select facet, count(*) n from pages where type='地点' and hidden=0
                      and slug not in (select slug from place_children)
                      group by facet order by n desc"""):
    print("   %-10s %d" % (r["facet"], r["n"]))
print("E 地点顶层合计:", c.execute(
    "select count(*) from pages where type='地点' and hidden=0 "
    "and slug not in (select slug from place_children)").fetchone()[0])
