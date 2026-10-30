# -*- coding: utf-8 -*-
"""核对：清单 676 与页面未定 415 的差额来源。"""
import io, json, os, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
scenes = {r["script"] for r in con.execute("select script from scenes")}


def page_place(sc):
    r = con.execute("select sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    if not r:
        return None
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息" and s.get("html"):
            t = s["html"]
            if "地点：" in t:
                b = t.split("地点：", 1)[1]
                return b.split("（依据：", 1)[0].strip()
    return ""


no_page, no_place, has_place = [], [], 0
for sc in scenes:
    pp = page_place(sc)
    if pp is None:
        no_page.append(sc)
    elif pp == "":
        no_place.append(sc)
    else:
        has_place += 1
print("scenes 表:", len(scenes))
print("无场景页:", len(no_page))
print("有页但无地点:", len(no_place))
print("有地点:", has_place)
print("\n无页面样例:", no_page[:10])
