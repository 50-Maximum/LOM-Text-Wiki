# -*- coding: utf-8 -*-
import io, sys, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
rows = c.execute("select name, slug, mentions from pages where type='人物'").fetchall()
pre = collections.Counter()
nopre = []
for nm, slug, m in rows:
    if "·" in nm:
        pre[nm.split("·")[0]] += 1
    else:
        nopre.append((nm, m))
print("有前缀 %d 人，无前缀 %d 人" % (sum(pre.values()), len(nopre)))
print("\n前缀分布：")
for p, k in pre.most_common():
    print("  %-10s %d" % (p, k))
print("\n无前缀（按引用数）：")
nopre.sort(key=lambda x: -(x[1] or 0))
out = ["%s(%d)" % (n, m) for n, m in nopre]
for i in range(0, len(out), 7):
    print("  " + "  ".join(out[i:i + 7]))
