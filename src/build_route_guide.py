# -*- coding: utf-8 -*-
"""把攻略年表的主线/支线标注落到具体剧本上，供事件页判定用（场景仍按脚本推导）。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
keep = json.load(open(B + r"\scene_time_ref.json", encoding="utf-8"))
tl = json.load(open(B + r"\ref_wiki\timeline.json", encoding="utf-8"))
g = {}
for r in tl:
    if r["kind"] not in ("主线", "支线"):
        continue
    for sc, v in keep.items():
        if v["name"] and v["name"] in r["event"]:
            g.setdefault(sc, r["kind"])
json.dump(g, open(B + r"\route_guide.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("落在剧本上的攻略标注 %d 条" % len(g))
for sc, k in g.items():
    print("   %-22s %s" % (sc, k))
