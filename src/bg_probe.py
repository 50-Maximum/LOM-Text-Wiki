# -*- coding: utf-8 -*-
"""从原始剧本里抽背景资源（LoadView / ViewName），看能不能用背景反推地点。"""
import io, os, re, json, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

RAW = r"D:\LegendOfMortal Wiki\data\raw\scripts"
PAT = re.compile(r'LoadView\(\s*"([^"]+)"|ViewName"\)\.value\s*=\s*"([^"]+)"')

bg = {}
files = 0
for fn in os.listdir(RAW):
    if not fn.lower().endswith(".txt"):
        continue
    sc = fn[:-4]
    try:
        s = open(os.path.join(RAW, fn), encoding="utf-8", errors="ignore").read()
    except Exception:
        continue
    files += 1
    names = []
    for m in PAT.finditer(s):
        v = m.group(1) or m.group(2)
        if v and v not in names:
            names.append(v)
    if names:
        bg[sc] = names

print("扫描文件:", files, "含背景的脚本:", len(bg))
cnt = collections.Counter(v for vs in bg.values() for v in set(vs))
print("不同背景数:", len(cnt))
print("出现最多的 15 个:", cnt.most_common(15))
print("\n样例:")
for sc in list(bg)[:8]:
    print("   %-22s %s" % (sc, bg[sc]))
json.dump(bg, open(r"D:\LegendOfMortal Wiki\data\scene_bg.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, sort_keys=True)
print("\n已写入 data/scene_bg.json")
