# -*- coding: utf-8 -*-
"""查 S0022_01 当前地点与来源，以及各推断文件里是否有它。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
D = os.path.join(BASE, "data")
con = sqlite3.connect(os.path.join(D, "wiki.db"))
con.row_factory = sqlite3.Row
r = con.execute("select slug,sections from pages where slug=?", ("场景/S0022_01",)).fetchone()
for s in json.loads(r["sections"] or "[]"):
    if s.get("h") == "场景信息":
        print("页面:", s.get("html"))

for f in ["place_manual.json", "place_override.json", "scene_place_infer.json", "place_logic.json",
          "place_infer2.json", "place_infer3.json", "place_infer4.json", "place_infer5.json",
          "place_infer6.json"]:
    p = os.path.join(D, f)
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        if "S0022_01" in d:
            print("  %-24s %s" % (f, d["S0022_01"]))
print("\nscenes 表 place:", con.execute("select place from scenes where script='S0022_01'").fetchone()[0])
