# -*- coding: utf-8 -*-
"""按事件编号查页面：名称、分类（地点）、剩余未命名。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
codes = ["Mall_Work_Result_BF_01", "Mall_Free_Result_N_01", "Center_Work_N_01",
         "Alchemy_Work_BF_01", "Study_Work_N_01", "Pharmacy_Work_E_01",
         "Door_Work_N_01", "Travel_F_02", "Section_02_03_03_S_01"]
for cd in codes:
    r = c.execute("select name,cats,infobox from pages where slug=?", ("地图事件/" + cd,)).fetchone()
    if not r:
        print("%-26s 无页" % cd)
        continue
    print("%-26s %-34s cats=%s" % (cd, r["name"], r["cats"]))

print("\n仍为「地点＋结果」:")
n = 0
for r in c.execute("select name,infobox from pages where type='地图事件'"):
    inf = json.loads(r["infobox"] or "{}")
    if inf.get("名称来源") == "地点＋结果":
        print("   ", r["name"], "|", inf.get("事件编号"), "|", inf.get("事件值") or "")
        n += 1
print("合计", n)
