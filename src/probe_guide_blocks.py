# -*- coding: utf-8 -*-
import io, sys, os, glob, re, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
d = r"D:\LegendOfMortal Wiki\data\guide"
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
titles = {}
for sc, t in c.execute("select script,title from scenes"):
    if t:
        titles[re.sub(r"\s+", "", t)] = sc
print("场景标题数:", len(titles))

blocks = []
for f in glob.glob(os.path.join(d, "*.txt")):
    t = open(f, encoding="utf-8", errors="replace").read()
    for b in t.split("####"):
        b = b.strip()
        if "触发条件" not in b or "事件内容" not in b:
            continue
        b = re.sub(r"^[\s|]+", "", b)
        m = re.search(r"第[一二三四]年", b)
        name = b[:m.start()] if m else ""
        name = re.sub(r"\s+", "", name)[:40]
        i = b.find("触发条件")
        j = b.find("事件内容", i)
        cond = b[i + 4: j] if j > i else ""
        cond = re.sub(r"\s+", "", cond)
        blocks.append((os.path.basename(f), name, cond))
print("含触发条件的块:", len(blocks))
hit = 0
miss = []
for f, name, cond in blocks:
    if name in titles:
        hit += 1
    else:
        miss.append((name, cond[:50]))
print("块名直接命中场景标题:", hit, "/", len(blocks))
print("\n未命中样例:", miss[:15])
print("\n命中样例:")
for f, name, cond in blocks:
    if name in titles:
        print("  %-16s -> %-22s | %s" % (name, titles[name], cond[:70]))
        if hit < 0:
            break
