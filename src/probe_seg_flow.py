# -*- coding: utf-8 -*-
"""看一个剧情段的场序与前后文，找可用于推导地点的线索（下山/回山/抵达/途中…）。"""
import io, sys, os, json, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(B, "data", "wiki.db")).cursor()
SG = json.load(open(os.path.join(B, "data", "story_segments.json"), encoding="utf-8"))
segs = {s["id"]: s for s in SG["segments"]}

# 找包含 S0003_02_02 的段
sid = SG["seg_of"].get("S0003_02_02")
print("段:", sid)
s = segs[sid]
print("场序:", s["scenes"])

for sc in s["scenes"]:
    t, p = c.execute("select title,coalesce(place,'') from scenes where script=?", (sc,)).fetchone()
    print("\n %-22s %-14s place=%s" % (sc, (t or "")[:14], p or "空"))
    for seq, sp, tx in c.execute("""select seq,speaker,text from lines where script=?
                                    order by seq limit 2""", (sc,)):
        print("   首 %s：%s" % ((sp or "")[:6], (tx or "").replace("\n", " ")[:70]))
    for seq, sp, tx in c.execute("""select seq,speaker,text from lines where script=?
                                    order by seq desc limit 1""", (sc,)):
        print("   末 %s：%s" % ((sp or "")[:6], (tx or "").replace("\n", " ")[:70]))
