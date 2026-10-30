# -*- coding: utf-8 -*-
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
r = c.execute("select name,lead,facet,infobox from pages where type='地点' and name like '%无羡%'").fetchone()
print("无羡居：", (r["name"], r["facet"], (r["lead"] or "")[:40]) if r else "无页")
r2 = c.execute("select name from pages where type='地点' and name='江陵'").fetchone()
print("江陵地点页：", r2["name"] if r2 else "无")
print("总页：", c.execute("select count(*) from pages").fetchone()[0])
print("地点页：", c.execute("select count(*) from pages where type='地点'").fetchone()[0])
