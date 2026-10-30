# -*- coding: utf-8 -*-
"""看「其他」里都是什么，以及上级缺失/消失的页。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("=== 类型=其他（全部地点） ===")
for r in c.execute("select name,facet,facet2,infobox,hidden from pages where type='地点' and facet2='其他' order by name"):
    inf = json.loads(r["infobox"] or "{}")
    print("  %-12s 区域=%-6s 上级=%-10s%s" % (r["name"], r["facet"], inf.get("上级") or "-",
                                            " [hidden]" if r["hidden"] else ""))
print("\n=== 子级但无上级字段 ===")
kids = {r[0] for r in c.execute("select slug from place_children")}
for r in c.execute("select slug,name,infobox from pages where type='地点' and hidden=0"):
    inf = json.loads(r["infobox"] or "{}")
    if r["slug"] in kids and not inf.get("上级"):
        print("  ", r["slug"])
print("\n=== 岳阳是否还在 ===")
print([dict(r) for r in c.execute("select slug,name,hidden from pages where name like '%岳阳%'")])
