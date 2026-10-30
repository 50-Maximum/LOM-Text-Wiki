# -*- coding: utf-8 -*-
"""核验嵌套分支渲染：取一个多簇场景，打印「择一分支」栏。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(BASE + r"\data\wiki.db")
c.row_factory = sqlite3.Row
mp = json.load(open(BASE + r"\data\scene_cluster_map.json", encoding="utf-8"))
multi = [sc for sc, v in mp.items() if len(v.get("all") or []) > 1]
print("多簇场景 %d 个，抽样：" % len(multi))

out = []
for sc in multi[:3]:
    r = c.execute("select name,sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    out.append("\n== %s %s（%d 个簇）" % (sc, r["name"] if r else "无页", len(mp[sc]["all"])))
    if not r:
        continue
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "择一分支":
            for x in (s.get("rows") or [])[:8]:
                out.append("   " + (x.get("note") or ""))

# 统计：全站含嵌套说明的页面数
n = 0
for r in c.execute("select sections from pages where type='场景'"):
    for s in json.loads(r[0] or "[]"):
        if s.get("h") == "择一分支":
            if any("其中还嵌套一组分支" in (x.get("note") or "") for x in (s.get("rows") or [])):
                n += 1
            break
out.append("\n全站显示嵌套分支组的场景页 %d 个" % n)
open(BASE + r"\data\_cluster_check.txt", "w", encoding="utf-8").write("\n".join(out))
print("ok")
