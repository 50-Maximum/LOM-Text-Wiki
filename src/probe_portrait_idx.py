# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
W = r"D:\LegendOfMortal Wiki\data"
idx = json.load(open(W + r"\portrait_index.json", encoding="utf-8"))
print("index 类型:", type(idx).__name__, "条数:", len(idx))
k = list(idx)[0]
print("样例:", k, "->", json.dumps(idx[k], ensure_ascii=False)[:200])
nm = json.load(open(W + r"\portrait_names.json", encoding="utf-8"))
print("\nnames 类型:", type(nm).__name__, "条数:", len(nm))
items = list(nm.items())[:5] if isinstance(nm, dict) else nm[:5]
for it in items:
    print("   ", json.dumps(it, ensure_ascii=False)[:200])
