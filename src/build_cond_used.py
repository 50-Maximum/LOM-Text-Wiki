# -*- coding: utf-8 -*-
"""扫描全部原始脚本，统计每个判定 id 被哪些场使用 → data/cond_used.json"""
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "scripts")
LIB = json.load(open(os.path.join(BASE, "data", "cond_lib.json"), encoding="utf-8"))
TOK = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")

used = {}
files = 0
for fn in os.listdir(RAW):
    if not fn.lower().endswith(".txt"):
        continue
    sc = fn[:-4]
    files += 1
    txt = open(os.path.join(RAW, fn), encoding="utf-8", errors="ignore").read()
    for t in set(TOK.findall(txt)):
        if t in LIB:
            used.setdefault(t, []).append(sc)

for k in used:
    used[k].sort()

json.dump(used, open(os.path.join(BASE, "data", "cond_used.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)
print("脚本 %d 个；被判定的 id %d 个" % (files, len(used)))
for k in ["Ch_6_7_1_004", "Ch_6_7_1_005", "Ch_6_7_1_006", "M60015_01", "M60006_01", "S_Beh_LT_60"]:
    print("  %-14s %s" % (k, used.get(k, [])[:5]))
