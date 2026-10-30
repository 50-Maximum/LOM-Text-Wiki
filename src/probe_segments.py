# -*- coding: utf-8 -*-
import io, sys, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("剧情段页", c.execute("select count(*) from pages where type='剧情段'").fetchone()[0])
print("总页", c.execute("select count(*) from pages").fetchone()[0])
rows = c.execute("select slug,lead from pages where type='剧情段' order by slug limit 3").fetchall()
for s, l in rows:
    print("  ", s, "|", l[:70])
print("\n有多场段的样例：")
for s, l in c.execute("""select slug,lead from pages where type='剧情段'
                         and lead like '%共 3 场%' limit 2"""):
    print("  ", s, "|", l[:90])
    d = c.execute("select sections from pages where slug=?", (s,)).fetchone()[0]
    for sec in json.loads(d):
        print("     [%s] %d 行" % (sec.get("h"), len(sec.get("rows") or [])))
        for r in (sec.get("rows") or [])[:4]:
            print("        -", (r.get("title") or r.get("note"))[:40], "|", r.get("slug") or r.get("script"))
