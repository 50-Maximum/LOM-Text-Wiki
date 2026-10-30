# -*- coding: utf-8 -*-
"""对 10 条无旁证的年表条目做旁证检查：场景所属「剧情阶段」是否与年表月份推得的阶段一致。"""
import io, sys, json, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
ref = json.load(open(B + r"\scene_time_ref.json", encoding="utf-8"))
CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6,
      "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12}
def arc_of_date(y, mo):
    if (y, mo) <= (1, 11): return "外姓弟子"
    if (y, mo) <= (2, 8):  return "南宫寿宴"
    if (y, mo) <= (2, 10): return "江陵围城"
    if (y, mo) <= (3, 4):  return "唐门衰败"
    if (y, mo) <= (3, 7):  return "比武招亲"
    if (y, mo) <= (4, 2):  return "武林大会"
    return "武林盟进攻唐门"

SUSPECT = ["S2001_01", "S0018_05", "kitchen_work_903", "ch2_4_10_3", "ch4_2_3_1",
           "S0502_01", "S2200_04_09", "S2300_01", "ch5_2_7_1", "S0204_01_04_01_01"]
ok = bad = 0
for sc in SUSPECT:
    v = ref.get(sc) or {}
    ym = re.search(r"第([\u4e00-\u9fa5]+)年", v.get("year") or "")
    mm = re.search(r"([\u4e00-\u9fa5]+)月", v.get("month") or "")
    y, mo = CN.get(ym.group(1), 0), CN.get(mm.group(1), 0)
    seg = c.execute("select facet from pages where type='场景' and slug=?",
                    ("场景/" + sc,)).fetchone()
    seg = (seg[0] if seg else "") or ""
    guess = arc_of_date(y, mo)
    flag = "一致" if seg == guess else "不一致"
    if seg == guess: ok += 1
    else: bad += 1
    print("%-24s 年表%d年%d月 → 阶段[%s] ｜ 页面标注[%s] ｜ %s ｜ %s"
          % (sc, y, mo, guess, seg or "-", flag, v.get("name")))
print("\n一致 %d，不一致 %d" % (ok, bad))
