# -*- coding: utf-8 -*-
"""ch4_6_6 之后这条链是怎么接的：段、跳转、分支，找出「剧情衔接」为空的原因。"""
import io, sys, json, os, re, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
SG = json.load(open(B + r"\story_segments.json", encoding="utf-8"))
SEGOF = SG.get("seg_of") or {}
SEG = {s["id"]: s for s in SG["segments"]}
c = sqlite3.connect(B + r"\wiki.db").cursor()
D = os.path.join(B, "raw", "scripts")

for sc in ("ch4_6_6", "ch4_6_7", "ch4_6_8", "ch4_6_9", "ch4_6_10", "ch4_6_11", "ch4_6_12"):
    sid = SEGOF.get(sc) or "-"
    s = SEG.get(sid) or {}
    t = c.execute("select title from scenes where script=?", (sc,)).fetchone()
    print("\n%s ｜ %s ｜ 段 %s ｜ 段内 %s" % (sc, (t[0] if t else "-"), sid, s.get("scenes")))
    print("   next_seg=%s next_scene=%s branches=%s"
          % (s.get("next_seg") or "-", s.get("next_scene") or "-",
             json.dumps(s.get("branches") or [], ensure_ascii=False)[:160]))
    p = os.path.join(D, sc + ".txt")
    if os.path.exists(p):
        t2 = open(p, encoding="utf-8", errors="replace").read().split("\n")
        nxt = [l.strip() for l in t2 if "SetNextScript" in l or "ChangeScene" in l]
        chs = [l.strip() for l in t2 if "= choose(" in l]
        print("   脚本跳转:", nxt[:4] or "-")
        print("   脚本选择:", chs[:2] or "-")
