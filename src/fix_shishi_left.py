# -*- coding: utf-8 -*-
"""补最后三个史实残留的归属。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
p = os.path.join(B, "chars_prefix.json")
cp = json.load(open(p, encoding="utf-8"))
cp.update({"成吉思汗": "江湖", "左思": "江湖", "纯阳真人": "全真派"})
json.dump(cp, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("已补：成吉思汗→江湖、左思→江湖、纯阳真人→全真派")
