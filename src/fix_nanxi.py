# -*- coding: utf-8 -*-
"""南溪简介：去掉梦境证据，换真实场景的原文。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\data\intros_char.json"
d = json.load(open(P, encoding="utf-8"))
k = "人物/南溪"
e = d[k]
old = "若赵活挑战盟主并吞并武林盟，她自陈只会打打杀杀；若西武林不胜，她坦言背叛武林盟早已做好觉悟，事后不过死路一条（2）。最终她向瑞笙表明帮西武林盟却不想他因自己心乱丧命，看穿瑞笙自污唱戏粗暴敷衍后道别离去。"
new = ("若赵活挑战盟主并吞并武林盟，她自陈只会打打杀杀。她当面向瑞笙说明自己不掺和的原由，"
       "直言从来不觉得武林盟是对的，愿意替那个身不由己的人站唐门这一边（2）。"
       "瑞笙败露后为避武林盟报复而自污，她当面点破其唱戏粗暴敷衍，说不愿见他糟蹋自己，就此别过（3）。")
assert old in e["text"], "旧句未命中"
e["text"] = e["text"].replace(old, new)
e["footnotes"] = [
    {"n": 1, "text": "南溪在客栈自称七星剑主一脉正统传人，以七星剑为证。",
     "script": "ch6_9_2_3",
     "quote": "在下南溪，有七星剑为证，吾乃岭南剑派七星剑主一脉正统传人。"},
    {"n": 2, "text": "南溪向瑞笙说明不掺和的原由，直言从来不觉得武林盟是对的。",
     "script": "ch8_6_3",
     "quote": "至于瑞郎，我先前不掺和的原因，你应该很清楚才对。我从来不觉得武林盟是对的。"},
    {"n": 3, "text": "南溪点破瑞笙为避武林盟报复而自污，说不愿见他糟蹋自己，就此别过。",
     "script": "ch8_7_2_2_1",
     "quote": "真笨拙啊……为了避免武林盟报复，到头来，你也只能学王帮主、温夫人自污。"},
]
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("已更新南溪，脚注 %d 条" % len(e["footnotes"]))
print(e["text"])
