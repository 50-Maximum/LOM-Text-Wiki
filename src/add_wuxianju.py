# -*- coding: utf-8 -*-
"""加地点：江陵·无羡居（知名酒楼）。"""
import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\place_edits.json"
d = json.load(open(p, encoding="utf-8"))
new = d.setdefault("new_places", [])
if not any(x.get("name") == "无羡居" for x in new):
    new.append({"name": "无羡居", "parent": "江陵",
                "lead": "无羡居是江陵城中一处知名酒楼。"})
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("已加入新地点：无羡居（上级 江陵）")
else:
    print("无羡居 已存在")
