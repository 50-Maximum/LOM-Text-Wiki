# -*- coding: utf-8 -*-
"""核验「择一分支」栏目。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row
m = json.load(open(r"D:\LegendOfMortal Wiki\data\scene_cluster_map.json", encoding="utf-8"))
print("归属场景:", len(m))
picked = list(m)[:4]
for sc in picked:
    r = con.execute("select name,sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    if not r:
        print(sc, "无页面")
        continue
    print("\n==", sc, r["name"])
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "择一分支":
            for x in (s.get("rows") or [])[:4]:
                print("   ", x.get("note", "")[:110])
