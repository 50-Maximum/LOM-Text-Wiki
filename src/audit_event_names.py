# -*- coding: utf-8 -*-
"""事件命名审计：找出名字是编号/代码/占位的事件与地图事件。"""
import io, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

rows = list(c.execute("select type,name,slug from pages where type in ('事件','地图事件')"))
print("事件条目 %d" % len(rows))
code = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
generic = re.compile(r"^(转场|结果|选项|事件)?\s*\d*$|未命名|待命名")
bad = [r for r in rows if code.match(r["name"] or "") or generic.match(r["name"] or "")]
print("疑似未命名/编号名 %d" % len(bad))
for r in bad[:12]:
    print("   %-6s %-22s %s" % (r["type"], r["name"][:20], r["slug"]))

print("\n地图事件条目:", c.execute("select count(*) from pages where type='地图事件'").fetchone()[0])
for r in c.execute("select name,slug from pages where type='地图事件' limit 8"):
    print("   ", r["name"], r["slug"])
