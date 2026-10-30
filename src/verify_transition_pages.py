# -*- coding: utf-8 -*-
"""核验转场节点页内容与总页数。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("总页", c.execute("select count(*) from pages").fetchone()[0])
print("场景页", c.execute("select count(*) from pages where type='场景'").fetchone()[0])

out = []
for sc in ["S0020_02_break_start_01", "S0209_01_02"]:
    r = c.execute("select name,lead,sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    if not r:
        out.append(sc + " 无页")
        continue
    out.append("\n== %s" % r["name"])
    out.append("   " + (r["lead"] or ""))
    for s in json.loads(r["sections"] or "[]"):
        h = s.get("h")
        if h == "场景信息":
            out.append("   [场景信息] " + (s.get("html") or ""))
        elif h in ("接下来", "被指向"):
            items = [x.get("note") for x in (s.get("rows") or [])][:4]
            out.append("   [%s] %s" % (h, " / ".join(items)))

# 死链检查：场景页里指向不存在的脚本
missing = 0
for r in c.execute("select slug,sections from pages where type='场景'"):
    for s in json.loads(r["sections"] or "[]"):
        for x in (s.get("rows") or []):
            sc = x.get("script") or ""
            if sc and not c.execute("select 1 from pages where slug=?", ("场景/" + sc,)).fetchone():
                missing += 1
out.append("\n仍然指向空页的链接 %d 条" % missing)
open(r"D:\LegendOfMortal Wiki\data\_transition_check.txt", "w", encoding="utf-8").write("\n".join(out))
print("ok")
