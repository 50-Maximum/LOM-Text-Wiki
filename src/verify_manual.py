# -*- coding: utf-8 -*-
"""核验：人工地点生效、回忆/梦境标注、新建地点页、094 标题。"""
import io, json, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row


def info(sc):
    r = con.execute("select sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    if not r:
        return "(无页面)"
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息":
            return s.get("html") or ""
    return ""


for sc in ["S0203_01", "S0208_05_02", "S0802_01", "S2200_02_02", "S8500_01_03",
           "casino_01_101", "ch2_4_1", "S2901_04_02_break_start_01"]:
    t = con.execute("select title from scenes where script=?", (sc,)).fetchone()
    print("%-28s %s\n    %s" % (sc, (t["title"] if t else ""), info(sc)))

print("\n新建地点页:")
for n in ["崆峒-半雨屏", "崆峒-大铁铺", "崆峒-无色广场赌坊"]:
    r = con.execute("select slug,lead from pages where name=?", (n,)).fetchone()
    print("   %-14s %s | %s" % (n, "有" if r else "缺", (r["lead"][:40] if r else "")))

# 覆盖统计
by = collections.Counter()
for r in con.execute("select sections from pages where type='场景'"):
    h = ""
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息":
            h = s.get("html") or ""
    if "场景性质：" in h:
        by["回忆/梦境"] += 1
    elif "地点：" in h:
        by["有地点"] += 1
    else:
        by["无地点"] += 1
print("\n覆盖:", dict(by))
