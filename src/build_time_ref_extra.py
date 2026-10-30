# -*- coding: utf-8 -*-
"""序章 8 行年表事件 → 剧本的人工确认结果，合并进 scene_time_ref.json。

依据（逐条已核对原文）：
  你，听过唐门吗？／初识唐升   ch1_1       开头即「你，听说过唐门吗？」，seq34/54 选项一致
  招募弟子结果               ch1_1       seq59 四个选项逐字一致（一个也没招到…抢走零用钱）
  照镜子                    ch1_1_break_option  seq24「还不算太差／内在更重要／实在是难看」
  惊吓指数                   S8300_01    场景标题即「惊吓指数」，伙房剧情
  初识唐布衣                 S9904_01    seq8「琴棋书画」+ seq18「人家只不过穿体面点」
  初识唐铮                   alchemy_001 炼丹房，seq3「我是来工作的。／正是找死，怎样？」
  四书事件(一)同门霸凌        S8400_01    seq13「好汉不吃眼前亏／老子跟你们拚了／据理力争」
  四书事件(二)蒙面人前辈       S8400_02    seq31/50 选项逐字一致 + 「暗器是什么」
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
P = B + r"\scene_time_ref.json"
ref = json.load(open(P, encoding="utf-8"))
before = len(ref)

EXTRA = [
    ("ch1_1",        "一", "四", "上", "你，听过唐门吗？／招募弟子结果", 8, "主线"),
    ("ch1_1_break_option", "一", "四", "上", "照镜子", 3, "支线"),
    ("S8300_01",     "一", "四", "上", "惊吓指数", 6, "支线"),
    ("S9904_01",     "一", "四", "上", "初识唐布衣", 5, "支线"),
    ("alchemy_001",  "一", "四", "上", "初识唐铮", 4, "支线"),
    ("S8400_01",     "一", "四", "中", "四书事件(一)同门霸凌", 4, "主线"),
    ("S8400_02",     "一", "四", "中", "四书事件(二)蒙面人前辈", 6, "主线"),
]

added = 0
for sc, y, m, x, name, score, kind in EXTRA:
    old = ref.get(sc)
    if old:
        if name not in (old.get("name") or ""):
            old["name"] = (old.get("name") or "") + "／" + name
        old["score"] = max(old.get("score") or 0, score)
        print("合并  %-20s → %s" % (sc, old["name"]))
    else:
        ref[sc] = {"year": y, "month": m, "xun": x, "name": name,
                   "score": score, "src": "选项原文直查"}
        added += 1
        print("新增  %-20s %s年%s月%s ｜ %s" % (sc, y, m, x, name))

json.dump(ref, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nscene_time_ref: %d → %d（新增 %d）" % (before, len(ref), added))
