# -*- coding: utf-8 -*-
"""① 只剔除「单条文案命中」的噪声（保留 2 条以上）；
② 用攻略年表的主线/支线标注与我们脚本推导的段分类对撞。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
ref = json.load(open(B + r"\scene_time_ref.json", encoding="utf-8"))
cal = json.load(open(B + r"\ref_wiki\calendar.json", encoding="utf-8"))

keep = {sc: v for sc, v in ref.items() if (v.get("score") or 0) >= 2}
drop = {sc: v for sc, v in ref.items() if (v.get("score") or 0) < 2}
json.dump(keep, open(B + r"\scene_time_ref.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("保留 %d，剔除噪声 %d：%s" % (len(keep), len(drop),
                                "、".join(v["name"] for v in drop.values())))

# 主线/支线对撞：年表 kind（主线/支线） vs 我们的 facet2
kind = {}
tl = json.load(open(B + r"\ref_wiki\timeline.json", encoding="utf-8"))
for r in tl:
    if r["kind"] in ("主线", "支线"):
        kind[r["event"]] = r["kind"]

seg = json.load(open(B + r"\story_segments.json", encoding="utf-8"))
route_of = seg.get("route_of") or {}
seg_of = seg.get("seg_of") or {}
c = sqlite3.connect(B + r"\wiki.db").cursor()
f2 = {slug.split("/")[-1]: f for slug, f in
      c.execute("select slug,facet2 from pages where type='场景'")}

same, diff = 0, []
for nm, k in kind.items():
    for sc, v in keep.items():
        if v["name"] == nm:
            ours = f2.get(sc) or route_of.get(sc) or ""
            if ours == k:
                same += 1
            else:
                diff.append((nm, k, ours, sc))
print("\n年表标了主/支线且能对上的：一致 %d，不一致 %d" % (same, len(diff)))
for nm, k, ours, sc in diff:
    print("   %-14s 年表:%s ｜我们:%s ｜%s" % (nm, k, ours, sc))
