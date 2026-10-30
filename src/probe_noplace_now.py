# -*- coding: utf-8 -*-
"""抽查：之前无地点的场景，现在场景信息显示什么。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for sc in ["S0208_05_02", "ch2_4_1_1", "ch2_4_8_5", "S8500_01_03", "birth_02_01"]:
    r = c.execute("select name,sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    if not r:
        print(sc, "无页")
        continue
    t = ""
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息":
            t = s.get("html") or ""
            break
    print("%-14s %s" % (sc, t[:120]))
