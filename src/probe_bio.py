# -*- coding: utf-8 -*-
import io, sys, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
n = c.execute("select count(*) from pages where type='人物' and infobox like '%生日%'").fetchone()[0]
print("带生日的角色:", n, "/", c.execute("select count(*) from pages where type='人物'").fetchone()[0])
for nm in ("唐布衣", "赵活", "叶云裳", "虞小梅", "邹博"):
    r = c.execute("select name,infobox from pages where name like ?", ("%" + nm,)).fetchone()
    if not r:
        print("  ", nm, "无页")
        continue
    inf = json.loads(r[1])
    print("  %-8s %s" % (r[0], {k: inf[k] for k in ("性别", "生日", "年龄") if k in inf}))
