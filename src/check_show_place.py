# -*- coding: utf-8 -*-
"""看这批判定在页面上实际显示的地点。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
for sc in ("ch2_5_2_3", "S9901_01", "ch2_8_1_2", "section_01_free_03_01", "ch2_5_1_1", "talk_brother3_06_02"):
    r = c.execute("select name, sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    if not r:
        print(sc, "缺页")
        continue
    txt = ""
    for s in json.loads(r[1] or "[]"):
        if s.get("h") == "场景信息" and s.get("html"):
            txt = s["html"]
    print("%-14s %-24s %s" % (sc, r[0], txt.replace("\n", " ")[:90]))
