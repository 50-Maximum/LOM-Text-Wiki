# -*- coding: utf-8 -*-
"""看 S784 段（大师兄卧榻）的构造：段内场次、出口、分支，以及 ch4_6_1x 各自的跳转。"""
import io, sys, json, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
SG = json.load(open(B + r"\story_segments.json", encoding="utf-8"))
SEG = {s["id"]: s for s in SG["segments"]}
c = sqlite3.connect(B + r"\wiki.db").cursor()

for sid in ("S784", "S783", "S785"):
    s = SEG.get(sid)
    if not s:
        continue
    print("\n=== %s ｜ %s ｜ route=%s" % (sid, s.get("title"), s.get("route")))
    print("   scenes:", s.get("scenes"))
    print("   last:", s.get("last"), "｜ next_seg:", s.get("next_seg") or "-",
          "｜ next_scene:", s.get("next_scene") or "-")
    print("   branches:", json.dumps(s.get("branches") or [], ensure_ascii=False)[:300])

print("\n=== ch4_6_1x 脚本里的跳转与选择")
import os
D = os.path.join(B, "raw", "scripts")
for fn in sorted(os.listdir(D)):
    if not re.match(r"^ch4_6_1[0-9]", fn):
        continue
    t = open(os.path.join(D, fn), encoding="utf-8", errors="replace").read().split("\n")
    nxt = [l.strip() for l in t if "SetNextScript" in l or "ChangeScene" in l]
    chs = [l.strip() for l in t if "= choose(" in l or "dicemenudialog" in l]
    print("  %-22s 跳转 %s ｜ 选择 %s" % (fn[:-4], nxt[:3] or "-", chs[:2] or "-"))
