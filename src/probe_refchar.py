# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
ch = json.load(open(B + r"\ref_wiki\characters.json", encoding="utf-8"))
print("类型", type(ch).__name__, "数量", len(ch))
k = list(ch)[0] if isinstance(ch, dict) else 0
print("样例键", k if isinstance(ch, dict) else "-")
print(json.dumps(ch[k] if isinstance(ch, dict) else ch[0], ensure_ascii=False, indent=1)[:700])
pre = json.load(open(B + r"\chars_prefix.json", encoding="utf-8"))
print("\nprefix 样例:", list(pre.items())[:5])
tit = json.load(open(B + r"\chars_title.json", encoding="utf-8"))
print("title 样例:", list(tit.items())[:5])
