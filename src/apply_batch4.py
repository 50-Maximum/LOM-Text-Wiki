# -*- coding: utf-8 -*-
"""第 4 批：20 场候选里，真错的 3 场（夺魄被当成铁拳门/门中闲谈的所在地）。"""
import io, json, os, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\place_override.json"
ov = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

BATCH = {
    "section_01_free_03_01": ("崆峒山-铁拳巷",
        "赵活到铁拳门上工打铁，原文「铁拳门最古老的手艺活，就是打铁」，铁拳门驻地在铁拳巷，不在夺魄森林"),
    "ch2_5_1_1": ("崆峒山",
        "留学门派抽签，魏菊告知抽中铁拳门，原文「论人数的话，是四门之中最多的」，场景在崆峒山而非某一门驻地"),
    "talk_brother3_06_02": ("唐门",
        "唐升向赵活介绍崆峒四掌门，是门中闲谈，正文无崆峒现场描写"),
}
for k, (pl, why) in BATCH.items():
    ov[k] = {"place": pl, "why": why}
json.dump(ov, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("覆盖表", len(ov), "条")
print(collections.Counter(v["place"] or "（不标）" for v in ov.values()).most_common())
