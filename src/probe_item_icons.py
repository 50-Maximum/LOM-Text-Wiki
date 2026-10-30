# -*- coding: utf-8 -*-
"""找物品图标名从哪来：raw 里搜 item_ / Sprite / 图标字段，并列出 system 下所有表。"""
import io, os, re, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

RAW = r"D:\LegendOfMortal Wiki\data\raw"
print("--- system 下的表 ---")
for f in sorted(os.listdir(os.path.join(RAW, "system"))):
    print("   ", f)

pat = re.compile(r"item_[a-z]+(?:_[a-z]+)?_\d+")
cnt = collections.Counter()
files = collections.Counter()
for dirpath, _, fs in os.walk(RAW):
    for f in fs:
        p = os.path.join(dirpath, f)
        try:
            s = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        for m in pat.findall(s):
            cnt[m] += 1
            files[f] += 1
print("\n--- item_* 命中 %d 种，文件 %d 个 ---" % (len(cnt), len(files)))
for k, v in cnt.most_common(15):
    print("   ", k, v)
print("   文件:", list(files)[:10])

# 立绘/图标字段关键词
for kw in ("Sprite", "icon", "Icon", "img", "portrait", "Portrait"):
    hits = []
    for dirpath, _, fs in os.walk(RAW):
        for f in fs:
            if not f.endswith(".txt"):
                continue
            p = os.path.join(dirpath, f)
            try:
                s = open(p, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            n = len(re.findall(kw, s))
            if n:
                hits.append((f, n))
    print("%-9s %s" % (kw, sorted(hits, key=lambda x: -x[1])[:5]))
