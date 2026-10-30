# -*- coding: utf-8 -*-
"""复核后改判：崆峒试招归南宫寿宴；唐门内务归外姓弟子；山贼支线归唐门衰败；梦境/丐帮支线不限期。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
p = os.path.join(B, "arcs.json")
d = json.load(open(p, encoding="utf-8"))
sc = d.setdefault("scene", {})

FIX = {
    # 崆峒留学期间（第2章＝南宫寿宴）
    "S0014_01_01": "南宫寿宴",
    "S0014_01_02": "南宫寿宴",
    "S2200_04_07": "南宫寿宴",
    # 唐门内务、杂役、团练（第1章＝外姓弟子）
    "S9001_01": "外姓弟子",
    "S9001_03": "外姓弟子",
    "S9001_04": "外姓弟子",
    "S0012_01_01": "外姓弟子",
    # 唐布衣带赵活打劫山贼（金国行刺之后，唐门衰败期）
    "S9904_01": "唐门衰败",
    "S9904_01_02": "唐门衰败",
    # 梦境与丐帮跑路支线，不与主线同步
    "S8500_01": "不限时间",
    "S8500_01_03": "不限时间",
    "S9906_01_01": "不限时间",
    "S9906_01_03_option": "不限时间",
}
for k, v in FIX.items():
    sc[k] = v
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("改判 %d 个场景" % len(FIX))
for k, v in FIX.items():
    print("   %-24s → %s" % (k, v))
