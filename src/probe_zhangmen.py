# -*- coding: utf-8 -*-
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
for r in c.execute("select slug,name,type from pages where name like '%掌门%' or name like '%无名角色%'"):
    print(r["slug"], "|", r["type"], "|", r["name"])
print("\nintros 键含 掌门：")
for fn in ("intros_char.json", "intros_world.json"):
    d = json.load(open(os.path.join(B, fn), encoding="utf-8"))
    print(" ", fn, [k for k in d if "掌门" in k][:8])
