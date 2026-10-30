# -*- coding: utf-8 -*-
"""记入五零口述：上官隼要把上官萤嫁到东瀛。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
p = os.path.join(B, "intros_char.json")
d = json.load(open(p, encoding="utf-8"))
node = d.get("人物/上官萤")
note = "上官隼有意把她嫁到东瀛。"
if isinstance(node, dict):
    t = node.get("text") or ""
    if note not in t:
        node["text"] = t + note
        print("上官萤 导语已补：", note)
else:
    d["人物/上官萤"] = {"text": note, "footnotes": []}
    print("上官萤 新建导语：", note)
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
