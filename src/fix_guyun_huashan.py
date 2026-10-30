# -*- coding: utf-8 -*-
"""清掉过期的孤云山导语；华山派导语改成不牵涉全真归属的写法。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"

p = os.path.join(B, "intros_world.json")
d = json.load(open(p, encoding="utf-8"))
for k in ["势力/孤云山", "孤云山"]:
    if k in d:
        d.pop(k)
        print("删除过期导语", k)
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

q = os.path.join(B, "extra_factions.json")
e = json.load(open(q, encoding="utf-8"))
if "华山派" in e:
    e["华山派"]["text"] = (
        "华山一派分两支。老华山派源出陈抟老祖，「神算子」周浊即系出这一支。"
        "另一支由郝大通开创：他精通老庄易经，算到华山有奇遇，得希夷祖师《睡功》后有所感悟，"
        "自成一家。养明道人裘志攘是华山派第二代弟子，孟珙年少习武时曾受他提点；"
        "后来裘志攘投了金人，孟珙在混战中认出这位旧识。")
    json.dump(e, open(q, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("华山派导语已重写")
