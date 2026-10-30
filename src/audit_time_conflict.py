# -*- coding: utf-8 -*-
"""scene_time 表（攻略索引推导）vs scene_time_ref.json（年表选项原文反查）冲突盘点。"""
import io, sys, json, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
print("scene_time 列:", [r[1] for r in c.execute("pragma table_info(scene_time)")])
rows = list(c.execute("select script,year,month,xun,event from scene_time"))
print("scene_time 行数 %d；样例 %s" % (len(rows), rows[:3]))

ref = json.load(open(B + r"\scene_time_ref.json", encoding="utf-8"))
CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6,
      "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12}
st = {r[0]: (r[1], r[2], r[3], r[4]) for r in rows}

conf, same, onlyref = [], 0, 0
for sc, v in ref.items():
    y = CN.get((re.search(r"第([\u4e00-\u9fa5]+)年", v.get("year") or "") or [None, ""])[1] if False else "", 0)
    ym = re.search(r"第([\u4e00-\u9fa5]+)年", v.get("year") or "")
    mm = re.search(r"([\u4e00-\u9fa5]+)月", v.get("month") or "")
    ay = CN.get(ym.group(1), 0) if ym else 0
    am = CN.get(mm.group(1), 0) if mm else 0
    if not (ay and am):
        continue
    if sc not in st:
        onlyref += 1
        continue
    s = st[sc]
    if (s[0], s[1]) == (ay, am):
        same += 1
    else:
        conf.append((sc, s, (ay, am), v.get("score"), v.get("name")))
print("\n两边都有：一致 %d，冲突 %d，仅年表 %d" % (same, len(conf), onlyref))
for sc, s, r, score, name in sorted(conf, key=lambda x: -(x[3] or 0)):
    print("   %-22s scene_time %s年%s月%s（%s） ｜ 年表 %s年%s月 ｜ score%s ｜ %s"
          % (sc, s[0], s[1], s[2], (s[3] or "")[:14], r[0], r[1], score, (name or "")[:20]))
