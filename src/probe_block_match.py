# -*- coding: utf-8 -*-
import io, sys, sqlite3, re, glob, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
evs = [n for (n,) in c.execute("select distinct name from notes where type='事件'")]
print("事件名:", len(evs))
blocks = []
for f in glob.glob(r"D:\LegendOfMortal Wiki\data\guide\*.txt"):
    t = open(f, encoding="utf-8", errors="replace").read()
    for b in t.split("####"):
        b = b.strip().lstrip("| ")
        if "触发条件" not in b or "事件内容" not in b:
            continue
        m = re.search(r"第[一二三四]年", b)
        name = re.sub(r"\s+", "", b[:m.start()] if m else "")[:30]
        i, j = b.find("触发条件"), b.find("事件内容")
        cond = re.sub(r"\s+", "", b[i + 4: j])
        if name:
            blocks.append((name, cond))
print("块:", len(blocks), " 唯一名:", len({b[0] for b in blocks}))
ex = [b for b in blocks if b[0] in evs]
print("精确命中事件名:", len(ex))
part = []
for nm, cond in blocks:
    if nm in evs:
        continue
    hits = [e for e in evs if nm in e or (len(nm) >= 4 and e in nm)]
    if hits:
        part.append((nm, hits[:2], cond[:40]))
print("包含关系命中:", len(part))
for x in part[:12]:
    print("   ", x[0], "->", x[1], "|", x[2])
print("\n精确命中样例:")
for nm, cond in ex[:10]:
    print("   ", nm, "|", cond[:60])
