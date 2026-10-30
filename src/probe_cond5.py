# -*- coding: utf-8 -*-
import io, sys, os, glob, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"D:\LegendOfMortal Wiki\data\raw"
allf = [p for p in glob.glob(os.path.join(base, "**", "*"), recursive=True) if os.path.isfile(p)]
print("总文件:", len(allf))
ext = collections.Counter(os.path.splitext(p)[1].lower() for p in allf)
print("扩展名:", ext.most_common(8))
dirs = collections.Counter(os.path.basename(os.path.dirname(p)) for p in allf)
print("目录 top:", dirs.most_common(10))

# 文件名含 event/schedule/action/main
for kw in ("event", "schedule", "action", "main", "loop", "manage", "condition", "check"):
    hits = [os.path.basename(p) for p in allf if kw in os.path.basename(p).lower()]
    print(f"\n文件名含 {kw}: {len(hits)} ->", hits[:12])

# 全库搜关键 API
tokens = ["GetStatData", "HasItem", "GetItemCount", "Random", "Probab", "chance", "Require", "CanTrigger", "IsEnable"]
print()
for tk in tokens:
    n = 0
    sample = None
    for p in allf:
        try:
            t = open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        if tk in t:
            n += 1
            if sample is None:
                for ln in t.splitlines():
                    if tk in ln:
                        sample = (os.path.basename(p), ln.strip()[:150])
                        break
    print(f"{tk}: {n} 文件 | {sample}")
