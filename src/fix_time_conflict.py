# -*- coding: utf-8 -*-
"""时间冲突处置：
   score>=5（多条选项逐字命中）→ 保留年表时间，让 build_wiki2 覆盖 scene_time
   score< 5（可能是「同一小事件在不同月份重复出现」）→ 删掉年表条目，保留 scene_time
"""
import io, sys, json, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
P = B + r"\scene_time_ref.json"
ref = json.load(open(P, encoding="utf-8"))
c = sqlite3.connect(B + r"\wiki.db").cursor()
st = {r[0]: (r[1], r[2]) for r in c.execute("select script,year,month from scene_time")}
CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6,
      "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12}

win, drop = [], []
for sc, v in list(ref.items()):
    ym = re.search(r"第([\u4e00-\u9fa5]+)年", v.get("year") or "")
    mm = re.search(r"([\u4e00-\u9fa5]+)月", v.get("month") or "")
    if not (ym and mm):
        continue
    ay, am = CN.get(ym.group(1), 0), CN.get(mm.group(1), 0)
    if sc not in st or (st[sc][0], st[sc][1]) == (ay, am):
        continue
    if (v.get("score") or 0) >= 5:
        win.append(sc)
    else:
        drop.append(sc)

for sc in drop:
    print("删年表条目 %-22s %s ｜ %s" % (sc, ref[sc]["name"], ref[sc].get("score")))
    ref.pop(sc)
json.dump(ref, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(win, open(B + r"\time_override.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n年表优先（覆盖 scene_time）%d 条：%s" % (len(win), "、".join(win)))
print("scene_time 优先（删年表）%d 条" % len(drop))
print("scene_time_ref 剩 %d 条" % len(ref))
