# -*- coding: utf-8 -*-
"""重建后核验：人工地点、回忆/梦境标注、标题覆盖、新场景、地点覆盖。"""
import io, json, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row


def info(sc):
    r = con.execute("select sections,name from pages where slug=?", ("场景/" + sc,)).fetchone()
    if not r:
        return "(无页面)"
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息":
            return (r["name"] or "") + " | " + (s.get("html") or "")
    return r["name"] or ""


for sc in ["S0022_01", "ch2_4_1", "S2901_04_02_break_start_01", "ch4_9_3_8_part_2",
           "ch8_8_1", "S0208_05_02"]:
    print("%-28s %s" % (sc, info(sc)))

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
print("\n场景覆盖:", dict(by))
print("页面总数:", con.execute("select count(*) from pages").fetchone()[0])
print("笔记数:", con.execute("select count(*) from notes").fetchone()[0])
print("势力归属:", con.execute("select count(*) from char_faction").fetchone()[0])
