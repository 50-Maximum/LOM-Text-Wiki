# -*- coding: utf-8 -*-
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
r = c.execute("select * from pages where name='孤云山'").fetchone()
print("slug", r["slug"], "type", r["type"], "facet", r["facet"], "cats", r["cats"], "mentions", r["mentions"])
print("lead", (r["lead"] or "")[:100])
print("\n== 所有含孤云山的页 ==")
for x in c.execute("select type,slug,name from pages where name like '%孤云山%'"):
    print("  ", x["type"], x["slug"], x["name"])
print("\n== data 里还有哪些文件提到 势力/孤云山 ==")
B = r"D:\LegendOfMortal Wiki\data"
for n in os.listdir(B):
    if not n.endswith(".json"):
        continue
    try:
        s = open(os.path.join(B, n), encoding="utf-8").read()
    except Exception:
        continue
    if "势力/孤云山" in s:
        print("  ", n, s.count("势力/孤云山"))
