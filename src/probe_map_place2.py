# -*- coding: utf-8 -*-
"""地图事件的地点该取剧本场景页的地点，而不是前缀猜。先看样例。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row
pm = json.load(open(os.path.join(BASE, "data", "position_script_map.json"), encoding="utf-8"))
fam = json.load(open(os.path.join(BASE, "data", "position_script_family.json"), encoding="utf-8"))
for code in ["Mall_Work_Result_BF_01", "Mall_Free_Result_N_01", "Center_Work_N_01",
             "Door_Work_N_01", "Alchemy_Work_BF_01", "Study_Work_N_01"]:
    sc = pm.get(code)
    print("\n==", code, "→", sc)
    if not sc:
        print("   无剧本映射")
        continue
    r = c.execute("select name,cats,sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    if not r:
        print("   无场景页")
        continue
    loc = ""
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息":
            loc = (s.get("html") or "")[:120]
    print("   页名:", r["name"], "| cats:", r["cats"])
    print("   场景信息:", loc)
