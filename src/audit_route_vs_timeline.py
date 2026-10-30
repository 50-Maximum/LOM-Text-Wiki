# -*- coding: utf-8 -*-
"""年表行里的长事件名，包含哪个已定位事件名，就用那一行判定主/支线。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
keep = json.load(open(B + r"\scene_time_ref.json", encoding="utf-8"))
tl = json.load(open(B + r"\ref_wiki\timeline.json", encoding="utf-8"))
c = sqlite3.connect(B + r"\wiki.db").cursor()
f2 = {slug.split("/")[-1]: f for slug, f in
      c.execute("select slug,facet2 from pages where type='场景'")}

same, diff, miss = 0, [], []
for r in tl:
    if r["kind"] not in ("主线", "支线"):
        continue
    hits = [(sc, v) for sc, v in keep.items() if v["name"] and v["name"] in r["event"]]
    if not hits:
        miss.append(r["event"][:30])
        continue
    for sc, v in hits[:3]:
        ours = f2.get(sc) or ""
        if not ours:
            continue
        if ours == r["kind"]:
            same += 1
        else:
            diff.append((v["name"], r["kind"], ours, sc))
print("对上年表行 %d 条事件；一致 %d，不一致 %d，未定位 %d"
      % (same + len(diff), same, len(diff), len(miss)))
for nm, k, ours, sc in diff[:12]:
    print("   %-14s 年表:%s ｜我们:%s ｜%s" % (nm, k, ours, sc))
print("\n未定位的年表行:", "、".join(miss[:10]))
