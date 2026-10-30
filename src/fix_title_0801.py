# -*- coding: utf-8 -*-
"""珠绳飞甲是铁匠的称号，不是来新子的。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"


def load(n):
    p = os.path.join(B, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def save(n, d):
    json.dump(d, open(os.path.join(B, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


ct = load("chars_title.json")
ct.pop("来新子", None)
ct["铁匠"] = "珠绳飞甲"
save("chars_title.json", ct)
print("称号：铁匠=珠绳飞甲，来新子 取消")

ic = load("intros_char.json")
for slug, txt in [
    ("人物/来新子",
     "铁冠道人的弃徒，火炎山剑阁第二炉锻长。他自称与剑阁铁氏兄弟同出一门，"
     "赵活却听出「跟我们认识的火炎山铁匠截然不同」。"),
    ("人物/铁匠",
     "眉山镇打铁的铁匠，本名朱兄，绰号珠绳飞甲。ch5_4_1 里他与南宫深比武，"
     "是市井里的寻常匠人，与火炎山剑阁无涉。"),
]:
    node = ic.get(slug)
    if isinstance(node, dict):
        node["text"] = txt
    else:
        ic[slug] = {"text": txt, "footnotes": []}
save("intros_char.json", ic)
print("两人简介已按称号修正")
