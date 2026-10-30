# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
cs = json.load(open(r"D:\LegendOfMortal Wiki\data\ref_wiki\characters.json", encoding="utf-8"))
has = lambda k: sum(1 for c in cs if (c.get("info") or {}).get(k))
print("人物", len(cs), "性别", has("性别"), "生日", has("生日"), "年龄", has("年龄"))
for c in cs[:3]:
    print("  ", c["title"], c.get("info"))
cal = json.load(open(r"D:\LegendOfMortal Wiki\data\ref_wiki\calendar.json", encoding="utf-8"))
from collections import Counter
print("\n年表", len(cal), Counter(x["year"] for x in cal).most_common())
print("  样例:", [x["name"] for x in cal[:8]])
