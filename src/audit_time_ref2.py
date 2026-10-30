# -*- coding: utf-8 -*-
"""给年表反查加严：文案分 + 标题重合度，双条件才保留。"""
import io, sys, json, sqlite3, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
ref = json.load(open(B + r"\scene_time_ref.json", encoding="utf-8"))
c = sqlite3.connect(B + r"\wiki.db").cursor()
title = {s: t for s, t in c.execute("select script,title from scenes")}

keep, drop = {}, []
for sc, v in ref.items():
    t = title.get(sc) or ""
    ov = difflib.SequenceMatcher(None, v["name"], t).ratio()
    ok = (v.get("score") or 0) >= 3 or ((v.get("score") or 0) >= 2 and ov >= 0.18)
    if ok:
        keep[sc] = v
    else:
        drop.append((sc, v, t, ov))
json.dump(keep, open(B + r"\scene_time_ref.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("保留 %d，剔除 %d" % (len(keep), len(drop)))
for sc, v, t, ov in drop[:15]:
    print("   剔除 %-24s %s（分 %d，标题重合 %.2f）场景:%s" % (
        sc, v["name"], v.get("score") or 0, ov, t[:20]))
