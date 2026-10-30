# -*- coding: utf-8 -*-
"""①判定库解析 Ch_6_6_2_Break_01_008 ②说 talk[11] 分支体里跳到哪。"""
import io, sys, gzip, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
p = os.path.join(B, "data", "mod_res", "LOMAssistant.conditions.json.gz")
raw = gzip.open(p, "rb").read().decode("utf-8")
d = json.loads(raw)
print("顶层键:", list(d.keys()))
for k in d:
    v = d[k]
    print("  %s: %s (%d)" % (k, type(v).__name__, len(v) if hasattr(v, "__len__") else -1))

for sect in ("Conditions", "Switches"):
    obj = d.get(sect) or {}
    hits = {k: v for k, v in obj.items() if "Ch_6_6_2_Break_01" in str(k)}
    print("\n%s 命中 %d 个" % (sect, len(hits)))
    for k, v in list(hits.items())[:6]:
        print("  ", k, "→", json.dumps(v, ensure_ascii=False)[:220])

print("\n=== talk[11] 分支体")
f = os.path.join(B, "data", "raw", "scripts", "ch6_6_2_break_start_01.txt")
s = open(f, encoding="utf-8", errors="replace").read()
i = s.find("elseif choice_talk == 11")
print(s[i:i + 900] if i >= 0 else "（没找到 elseif 11）")
print("\n=== 该剧本所有跳转")
for m in re.finditer(r'(SetNextScript|ChangeScene)\("([^"]+)"', s):
    print("  ", m.group(1), m.group(2))
