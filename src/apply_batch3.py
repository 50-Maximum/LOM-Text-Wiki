# -*- coding: utf-8 -*-
"""第 3 批：剩 11 场核定（有证据给地点，没证据就留空并写明原因）。"""
import io, os, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
p = os.path.join(BASE, "data", "place_override.json")
ov = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

BATCH = {
    "S0703_01": ("唐门", "唐门弟子来报飞石帮主递帖，「人在茶肆等，可要许他们上山吗」，赵活拒见"),
    "ch5_4_2": ("唐门-练功场", "旁白「练武场上，各路少年侠士各显神通」，唐升以掌门身分在场，比武为唐门小师妹择婿"),
    "S0101_01": ("上官交引舖", "上官萤处理交引舖拿货与保证金事，训斥沧帮弟子交不出货还想涨价"),
    # 以下看过原文仍无地点证据，明确留空，不再挂错的势力名
    "S8300_01_02": ("", "唐布衣与赵活打完飞石帮喽啰后擦药闲谈，未写所在何地"),
    "S2321_04_02_01": ("", "孟仙谣以「本县主」自居问江陵来军之事，未写是哪一县"),
    "S9904_01": ("", "山贼自陈「绕远路到这偏僻小镇」，场景在唐门地界外的小镇，镇名未交代"),
    "ch3_5_3_7_1": ("", "旁白只写「撤退到邻镇」，镇名与隶属未交代"),
    "ch4_5_2": ("", "郁竹在途中请唐布衣随行，只提到「此处的青楼」，未写城名"),
    "ch6_8_2_3_2": ("", "南宫深与赵活论家事，仅提「我下山去后会在岳阳多留一日」，未写当下所在"),
    "talk_girl5_02_06": ("", "夏侯兰逼上官萤代父领死，正文只提崆峒往事，未写当下所在"),
    "pharmacy_work_501": ("", "坐诊工作场景，正文只写飞石帮患者求诊，未写是哪间药铺"),
}
for k, (pl, why) in BATCH.items():
    ov[k] = {"place": pl, "why": why}
json.dump(ov, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("覆盖表 %d 条" % len(ov))
import collections
print(collections.Counter(v["place"] or "（不标）" for v in ov.values()).most_common())
