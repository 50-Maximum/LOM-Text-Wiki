# -*- coding: utf-8 -*-
"""唐布衣补漏：卧云岗一战他其实输了，且重伤垂危。
（这条是别名审计带出来的——只搜「石公远」「金乌」都没命中，场景标题写的是「大师兄败于飞石帮主」。）"""
import io, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\data\intros_char.json"
d = json.load(open(P, encoding="utf-8"))
v = d["人物/唐布衣"]

anchor = "铁臂神拳也挨不着唐布衣的衣角（9）。"
add = ("这一战他终究输了：卧云岗众目睽睽之下败在石公远手上，胸骨寸裂（18），"
       "回山时昏迷不醒、性命垂危（19）。")
if anchor in v["text"] and "胸骨寸裂" not in v["text"]:
    v["text"] = v["text"].replace(anchor, anchor + add)

have = {f.get("n") for f in (v.get("footnotes") or [])}
for n, t, sc, q in [
    (18, "卧云岗败于飞石帮主", "ch4_6_7_break_start_01", "大师兄竟然输了……输给了飞石帮主。"),
    (19, "败后重伤、胸骨寸裂、性命垂危", "ch4_6_6",
     "据悉，是在卧云岗众目睽睽之下，败于飞石帮主之手，才受的重伤。 大师兄胸骨寸裂，确是被极霸道的外门硬功所伤不假。"),
]:
    if n not in have:
        v["footnotes"].append({"n": n, "text": t, "script": sc, "quote": q})

json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("唐布衣 %d 字 / 脚注 %d" % (len(v["text"]), len(v["footnotes"])))
