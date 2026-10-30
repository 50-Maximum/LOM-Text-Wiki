# -*- coding: utf-8 -*-
"""盘点用户点名的人物/地点现状：页名、分类（势力）、是否有重复条目。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row

KEYS = ["铁拳门", "长老", "叶云啾", "鞠冬音", "鞠师姐", "阿花", "阎尖锐", "阎掌门",
        "野利察汉", "李云弃", "赵活师父", "夏侯兰", "赵师兄", "赖某人", "赖裕廷",
        "许胜", "觉空", "老和尚", "无相祖师", "叶云裳", "小梅", "赵活"]
print("== 人物页 ==")
seen = set()
for k in KEYS:
    for r in c.execute("select slug,name,cats,infobox from pages where type='人物' and name like ?", ("%" + k + "%",)):
        if r["slug"] in seen:
            continue
        seen.add(r["slug"])
        inf = json.loads(r["infobox"] or "{}")
        print("   %-26s | %-10s | %s | %s" % (r["name"], inf.get("势力") or "-", r["cats"], r["slug"]))

print("\n== 地点页（相关） ==")
for k in ["半雨屏", "大铁铺", "无色广场", "崆峒山", "福建", "福州"]:
    for r in c.execute("select slug,name,infobox,cats from pages where type='地点' and name like ?", ("%" + k + "%",)):
        inf = json.loads(r["infobox"] or "{}")
        print("   %-22s | 上级 %-10s | %s" % (r["name"], inf.get("上级") or "-", r["slug"]))

print("\n== 人物总数 ==", c.execute("select count(*) from pages where type='人物'").fetchone()[0])
