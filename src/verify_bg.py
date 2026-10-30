# -*- coding: utf-8 -*-
"""核验背景资源：条目数、场景页背景字段、覆盖率变化，并抽样看一条。"""
import io, json, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

print("背景资源条目:", c.execute("select count(*) from pages where type='背景资源'").fetchone()[0])
r = c.execute("select slug,lead,sections from pages where type='背景资源' "
              "order by cast(replace(infobox,'','') as text) limit 3").fetchall()
for x in r[:3]:
    secs = json.loads(x["sections"] or "[]")
    print("   %-24s %s | %s" % (x["slug"], x["lead"], [(s["h"], len(s.get("rows") or [])) for s in secs]))

# 场景页背景字段
n_bg = 0
for x in c.execute("select infobox from pages where type='场景'"):
    inf = json.loads(x["infobox"] or "{}")
    if inf.get("背景"):
        n_bg += 1
print("场景页带背景字段:", n_bg)

# 覆盖率
by_ev = collections.Counter()
for x in c.execute("select sections from pages where type='场景'"):
    txt = ""
    for s in json.loads(x["sections"] or "[]"):
        if s.get("h") == "场景信息" and s.get("html"):
            txt = s["html"]
    if "地点：" not in txt:
        by_ev["（无地点）"] += 1
        continue
    body = txt.split("地点：", 1)[1]
    ev = body.split("（依据：", 1)[1].rsplit("）", 1)[0] if "（依据：" in body else ""
    by_ev[ev] += 1
print("覆盖率:")
for k, v in by_ev.most_common(6):
    print("   %-16s %d" % (k, v))
