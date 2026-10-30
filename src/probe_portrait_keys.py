# -*- coding: utf-8 -*-
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
idx = json.load(open(r"D:\LegendOfMortal Wiki\data\portrait_index.json", encoding="utf-8"))
keys = sorted(idx)
print("总", len(keys))
print("前 40:", keys[:40])
zh = [k for k in keys if re.search(r"[\u4e00-\u9fff]", k)]
print("中文键:", len(zh), zh[:10])
for probe in ("zhao", "tang", "ye", "long", "xiaomei", "shifu", "wei", "yu"):
    print(probe, "->", [k for k in keys if probe in k.lower()][:6])
