# -*- coding: utf-8 -*-
"""唐布衣：把「回山」写实——是被青城道长护送回唐门（ch4_6_6）。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\data\intros_char.json"
d = json.load(open(P, encoding="utf-8"))
v = d["人物/唐布衣"]
old = "回山时昏迷不醒、性命垂危（19）"
new = "被青城诸位道长护送到唐门之后，昏迷不醒、性命垂危（19）"
if old in v["text"]:
    v["text"] = v["text"].replace(old, new)
for fn in v["footnotes"]:
    if fn.get("n") == 19:
        fn["quote"] = "幸得青城诸位道长出手护送，回返本门。"
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("已改地点表述：", new in v["text"])
