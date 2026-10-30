# -*- coding: utf-8 -*-
"""路线骨架：每个路线旗标由哪些场景设置、被哪些场景要求。"""
import json, os, sys, io, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
flags = json.load(open(os.path.join(BASE, "data", "scene_flags.json"), encoding="utf-8"))
titles = {r[0]: (r[1], r[2]) for r in c.execute("select script,title,chapter from scenes")}

ROUTE = {
    "G11000": "小师妹", "G11001": "上官萤", "G11002": "叶云裳", "G11003": "龙湘",
    "G11004": "小梅", "G11005": "小兰", "G11006": "小竹", "G11007": "小菊",
    "M20008": "留学", "M40036": "卧云岗", "M20028": "离家出走", "M60016": "武林大会",
    "M70052": "顽抗", "M30014": "玄功传承", "M50024": "叶云裳结缘前置",
}

for fid, name in ROUTE.items():
    sets = []
    for sid, v in flags.items():
        if fid in v.get("sets", {}):
            sets.append((sid, v["sets"][fid]))
    req = [sid for sid, v in flags.items()
           if any(r.get("flag") == fid and r.get("op") in (">=", ">", "=") for r in v.get("requires", []))]
    print(f"\n== {fid} {name} ==  设置 {len(sets)} 场 / 要求 {len(req)} 场")
    for sid, vals in sets[:6]:
        t, ch = titles.get(sid, ("?", "?"))
        print(f"   设 {sid} = {vals}  《{t}》 {ch}")
    for sid in req[:6]:
        t, ch = titles.get(sid, ("?", "?"))
        print(f"   需 {sid}  《{t}》 {ch}")
