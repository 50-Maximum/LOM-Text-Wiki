# -*- coding: utf-8 -*-
"""修正唐升脚注3：原句被 {size=24} 标签切断，引文改为连续片段。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\data\intros_char.json"
d = json.load(open(P, encoding="utf-8"))
v = d["人物/唐升"]
old = "他办事一律照门规。处置犯错的同门师长时，他说得明白：「按门规，当由掌刑使施罚。纵令我手执掌门令牌，亦不得擅自处置同门师长」（3）。"
new = "他办事一律照门规。处置犯错的同门师长时，他说「按门规，当由掌刑使施罚」，即便手执掌门令牌，也不得擅自处置同门师长（3）。"
v["text"] = v["text"].replace(old, new)
for fn in v["footnotes"]:
    if fn.get("n") == 3:
        fn["quote"] = "按门规，当由掌刑使施罚。"
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("已修正：%s" % ("成功" if new in v["text"] else "未替换"))
