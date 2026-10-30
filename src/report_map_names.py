# -*- coding: utf-8 -*-
"""输出地图事件命名的最终报告（写文件，避免控制台乱码）。"""
import io, json, sqlite3, sys, collections
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
out = []
rows = list(c.execute("select name,slug,infobox,cats from pages where type='地图事件' and slug!='地图事件/索引'"))
cnt = collections.Counter()
for r in rows:
    inf = json.loads(r["infobox"] or "{}")
    cnt[inf.get("名称来源") or "原生标题"] += 1
out.append("地图事件总数 %d" % len(rows))
for k, v in cnt.most_common():
    out.append("  %s: %d" % (k, v))
out.append("")
out.append("地点页 %d / 全部页面 %d" % (
    c.execute("select count(*) from pages where type='地点'").fetchone()[0],
    c.execute("select count(*) from pages").fetchone()[0]))
out.append("")
out.append("抽样：")
for r in rows[:24]:
    out.append("  %-40s [%s]" % (r["name"], r["cats"]))
open(r"D:\LegendOfMortal Wiki\data\_map_report.txt", "w", encoding="utf-8").write("\n".join(out))
print("ok")
