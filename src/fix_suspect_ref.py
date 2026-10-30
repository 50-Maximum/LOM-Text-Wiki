# -*- coding: utf-8 -*-
"""10 条可疑年表条目的处置：若该剧本已有 scene_time（攻略索引推导的时间），删年表条目不丢信息。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
P = B + r"\scene_time_ref.json"
ref = json.load(open(P, encoding="utf-8"))
c = sqlite3.connect(B + r"\wiki.db").cursor()
st = {r[0]: (r[1], r[2], r[3], r[4])
      for r in c.execute("select script,year,month,xun,event from scene_time")}

SUSPECT = ["S2001_01", "S0018_05", "kitchen_work_903", "ch2_4_10_3", "ch4_2_3_1",
           "S0502_01", "S2200_04_09", "S2300_01", "ch5_2_7_1", "S0204_01_04_01_01"]
drop, keep = [], []
for sc in SUSPECT:
    v = ref.get(sc)
    if not v:
        print("  跳过 %s（不在年表里）" % sc); continue
    if sc in st:
        s = st[sc]
        print("  删 %-24s 年表%s%s%s「%s」→ 保留 scene_time %s年%s月%s（%s）"
              % (sc, v["year"], v["month"], v["xun"], v["name"],
                 s[0], s[1], s[2], (s[3] or "")[:16]))
        ref.pop(sc)
        drop.append(sc)
    else:
        print("  留 %-24s 年表%s%s%s「%s」（scene_time 无此剧本）"
              % (sc, v["year"], v["month"], v["xun"], v["name"]))
        keep.append(sc)
json.dump(ref, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(drop, open(B + r"\time_ref_dropped.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n删除 %d 条，保留 %d 条；scene_time_ref 现 %d 条" % (len(drop), len(keep), len(ref)))
