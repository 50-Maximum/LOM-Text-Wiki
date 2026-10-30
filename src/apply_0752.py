# -*- coding: utf-8 -*-
"""五零 07:52 指令：唐姓改名、瑞笙/万里鹏程归杏花林、夏侯梅并义、全胜利改火炎山、叶辰简介重写。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"


def load(n):
    p = os.path.join(B, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def save(n, d):
    json.dump(d, open(os.path.join(B, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# 1) 唐姓改名
cf = load("chars_fix.json")
mg = cf.setdefault("merge", {})
mg["皮康"] = "唐皮康"
mg["许亚霆"] = "唐许亚霆"
mg["夏侯梅"] = "夏侯兰"
save("chars_fix.json", cf)
print("并义：皮康→唐皮康、许亚霆→唐许亚霆、夏侯梅→夏侯兰")

# 2) 归属：瑞笙、万里鹏程 → 杏花林；全胜利 → 火炎山剑阁
cp = load("chars_prefix.json")
cp.update({"唐皮康": "唐门", "唐许亚霆": "唐门", "瑞笙": "杏花林",
           "万里鹏程": "杏花林", "瑞杏": "杏花林", "全胜利": "火炎山剑阁",
           "铁拳弟子": "铁拳门", "铁拳门弟子": "铁拳门"})
save("chars_prefix.json", cp)
print("归属：瑞笙/万里鹏程→杏花林，全胜利→火炎山剑阁，铁拳弟子→铁拳门")

# 3) 简介：叶辰、唐皮康、唐许亚霆、瑞笙补注
ic = load("intros_char.json")


def set_text(slug, text):
    node = ic.get(slug)
    if isinstance(node, dict):
        node["text"] = text
    else:
        ic[slug] = {"text": text, "footnotes": []}


set_text("人物/叶辰",
         "叶辰是个被抢着冒充的名号。ch6_5_1 一场闹剧里，先后有三个人自称叶辰："
         "一名少侠说「在下叶辰」，另一名少侠说「我也叫叶辰」，接着一名峨嵋弟子也喊「我也叫叶辰」；"
         "旁观的点苍弟子只骂「哪来这么多叶辰」。至于真正的叶辰师出何门，原文通篇没有交代。")

for nm, ben in [("唐皮康", "皮康"), ("唐许亚霆", "许亚霆")]:
    node = ic.get("人物/" + nm)
    txt = "唐门弟子，本名%s，入门后改宗姓唐。" % ben
    if isinstance(node, dict):
        node["text"] = txt + (node.get("text") or "")
    else:
        ic["人物/" + nm] = {"text": txt, "footnotes": []}

save("intros_char.json", ic)
print("简介已写：叶辰、唐皮康、唐许亚霆")
