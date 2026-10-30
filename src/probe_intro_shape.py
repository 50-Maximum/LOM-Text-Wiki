# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
intro = json.load(open(B + r"\intros_char.json", encoding="utf-8"))
print("条目 %d" % len(intro))
for k in ("人物/唐衫", "人物/赵活", "唐衫"):
    if k in intro:
        print("\n键", k, "→ 类型", type(intro[k]).__name__)
        print(json.dumps(intro[k], ensure_ascii=False, indent=1)[:900])
print("\n键样例:", list(intro)[:6])
