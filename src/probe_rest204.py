# -*- coding: utf-8 -*-
"""看剩下 204 条「地点＋结果」的实际剧本内容，判断有没有可能起名。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row
pm = json.load(open(os.path.join(BASE, "data", "position_script_map.json"), encoding="utf-8"))
rows = [r for r in c.execute("select name,slug,infobox from pages where type='地图事件' and slug!='地图事件/索引'")]
n = 0
for r in rows:
    inf = json.loads(r["infobox"] or "{}")
    if (inf.get("名称来源") or "") != "地点＋结果":
        continue
    code = inf.get("事件编号")
    sc = pm.get(code)
    txt = ""
    if sc:
        rr = c.execute("select text,speaker from lines where script=? order by seq limit 1", (sc,)).fetchone()
        if rr:
            txt = (rr["text"] or "")[:70]
    print("%-26s %-14s %s" % (r["name"], sc or "-", txt))
    n += 1
    if n >= 18:
        break
