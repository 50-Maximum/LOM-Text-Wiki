# -*- coding: utf-8 -*-
"""路线聚类：每个路线旗标 → 要求场景、设置场景、共现旗标。
产出 data/routes_raw.json，供 LLM 写路线页。
"""
import json, os, sys, io, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
flags = json.load(open(os.path.join(BASE, "data", "scene_flags.json"), encoding="utf-8"))
scenes = {r[0]: {"title": r[1], "chapter": r[2], "lines": r[3], "place": r[4]}
          for r in c.execute("select script,title,chapter,line_count,place from scenes")}

ROUTE = {
    "G11000": "小师妹", "G11001": "上官萤", "G11002": "叶云裳", "G11003": "龙湘",
    "G11004": "小梅", "G11005": "小兰", "G11006": "小竹", "G11007": "小菊",
    "M20008": "留学", "M40036": "卧云岗", "M20028": "离家出走", "M60016": "武林大会",
    "M70052": "顽抗", "M50024": "叶云裳结缘前置",
}

def first_lines(script, n=24):
    rows = c.execute("select speaker,text from lines where script=? and text<>'' order by seq limit ?",
                     (script, n)).fetchall()
    return "\n".join(f"{sp}：{tx.replace(chr(10),' ')[:60]}" for sp, tx in rows)

out = {}
for fid, name in ROUTE.items():
    req = [sid for sid, v in flags.items()
           if any(r.get("flag") == fid and r.get("op") in (">=", ">", "=") for r in v.get("requires", []))]
    setsc = [(sid, v["sets"][fid]) for sid, v in flags.items() if fid in v.get("sets", {})]
    # 共现：同一场景还要求了哪些路线旗标
    co = collections.Counter()
    for sid in req:
        for r in flags[sid]["requires"]:
            if r["flag"] in ROUTE and r["flag"] != fid and r["op"] in (">=", ">", "="):
                co[r["flag"]] += 1
    pack = {
        "flag": fid, "name": name,
        "requires": [{"script": s, "title": scenes.get(s, {}).get("title", s),
                      "chapter": scenes.get(s, {}).get("chapter", ""),
                      "lines": scenes.get(s, {}).get("lines", 0)} for s in req],
        "sets": [{"script": s, "values": v, "title": scenes.get(s, {}).get("title", s),
                  "chapter": scenes.get(s, {}).get("chapter", ""),
                  "opening": first_lines(s)} for s, v in setsc],
        "cooccur": [{"flag": k, "name": ROUTE[k], "n": n} for k, n in co.most_common(6)],
    }
    out[fid] = pack
    print(f"{fid} {name}: 需 {len(req)} 场 / 设 {len(setsc)} 场 / 共现 {pack['cooccur'][:3]}")

json.dump(out, open(os.path.join(BASE, "data", "routes_raw.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("写出 routes_raw.json")
