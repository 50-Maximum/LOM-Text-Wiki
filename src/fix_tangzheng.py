# -*- coding: utf-8 -*-
"""订正唐铮条目。"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\data\intros_char.json"
d = json.load(open(P, encoding="utf-8"))
d["人物/唐铮"] = {
    "text": "唐门师兄，掌刑使，行事狠辣，擅用毒与拷问。早年在谭霸刀船上逼问官饷旧案，又暗中给绿林草莽下慢性毒药；对赵活始终疑心，屡次以毒立威。后来他叛出唐门，逼掌门服下尸心丹、夺走碧血玉，又以掌门性命要挟唐门，是门内最险的一条暗线。",
    "sources": [
        {"script": "ch4_3_8_4", "quote": "唐掌门的性命，已在我支配之下，碧血玉也终于到了我手中！", "note": "逼掌门服丹"},
        {"script": "ch4_4_2_break_start_01", "quote": "我说的是叛徒唐铮。", "note": "叛出唐门"},
        {"script": "ch2_4_6_4", "quote": "弟子信不过这群绿林草莽，是以自作主张，暗中下了慢性毒药。", "note": "暗下毒药"},
    ],
}
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("唐铮条目已更新")
