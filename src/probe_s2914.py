# -*- coding: utf-8 -*-
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
for sc in ["S2914_01", "S2002_01", "S2002_04"]:
    r = c.execute("select script,chapter,title,place from scenes where script=?", (sc,)).fetchone()
    print("==", sc, "| 章:", r["chapter"] if r else "-", "| 题:", (r["title"] if r else "-"))
sc_conds = json.load(open(os.path.join(B, "scene_conds.json"), encoding="utf-8"))
for k in ["S2002_01", "S2002_02", "S2002_04", "S2914_01"]:
    v = sc_conds.get(k)
    print("== scene_conds", k, ":", json.dumps(v, ensure_ascii=False)[:300] if v else "无")
