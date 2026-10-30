# -*- coding: utf-8 -*-
"""第 6 批核验：并义、眉山镇、八场改判。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row


def secs(slug):
    r = c.execute("select sections, infobox, name from pages where slug=?", (slug,)).fetchone()
    if not r:
        return None, None, None
    return json.loads(r["sections"] or "[]"), json.loads(r["infobox"] or "{}"), r["name"]


print("A. 并义标记条目数:", c.execute(
    "select count(*) from pages where infobox like '%兼为地点与势力%'").fetchone()[0])
for slug in ("地点/唐门", "势力/唐门"):
    s, i, nm = secs(slug)
    print("   %-12s %s | 性质=%s | 栏目=%d" % (slug, nm, i.get("性质"), len(s or [])))

s, i, nm = secs("地点/眉山")
print("B. 地点/眉山 下辖:", i.get("下辖"))
for x in s or []:
    if x.get("h") == "下辖地点":
        print("   ", [(r.get("title"), r.get("slug")) for r in x.get("rows") or []])
s2, i2, nm2 = secs("地点/眉山镇")
print("C. 地点/眉山镇:", nm2, "|", i2)

print("D. 八场改判：")
for sc in ("S8300_01_02", "S2321_04_02_01", "ch3_5_3_7_1", "ch4_5_2",
           "ch6_8_2_3_2", "talk_girl5_02_06", "pharmacy_work_501", "ch2_4_4_1"):
    r = c.execute("select sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    txt = ""
    for x in json.loads(r["sections"] or "[]"):
        if x.get("h") == "场景信息" and x.get("html"):
            txt = x["html"]
    print("   %-16s %s" % (sc, txt[:80]))
