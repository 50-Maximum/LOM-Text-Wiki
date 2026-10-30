# -*- coding: utf-8 -*-
"""抽检年表反查结果：低分命中、一剧本多事件、标题对不上。"""
import io, sys, json, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
ref = json.load(open(B + r"\scene_time_ref.json", encoding="utf-8"))
cal = json.load(open(B + r"\ref_wiki\calendar.json", encoding="utf-8"))
c = sqlite3.connect(B + r"\wiki.db").cursor()
title = {s: t for s, t in c.execute("select script,title from scenes")}

# 同一剧本被多个事件占用
cnt = collections.Counter()
for sc, v in ref.items():
    cnt[sc] += 1
dup = [sc for sc, n in cnt.items() if n > 1]
print("命中剧本 %d 个；被重复占用 %d 个" % (len(ref), len(dup)))

# 低分（score=1）
low = [(sc, v) for sc, v in ref.items() if (v.get("score") or 0) <= 1]
print("\n=== 低分命中 %d 条（需人工看）" % len(low))
for sc, v in low[:25]:
    print("   %-26s %s%s%s %-12s ｜场景：%s" % (sc, v["year"], v["month"], v["xun"],
                                                v["name"], (title.get(sc) or "（无场景）")[:24]))

print("\n=== 高分命中样例")
for sc, v in sorted(ref.items(), key=lambda x: -(x[1].get("score") or 0))[:8]:
    print("   %d分 %-24s %s %-12s ｜%s" % (v["score"], sc, v["month"], v["name"],
                                          (title.get(sc) or "")[:24]))
