# -*- coding: utf-8 -*-
"""对候选别名对做共现核查：同一场景同时出现两个名字 = 强证据（可能同人，也可能不同人）。"""
import io, sys, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
pairs = []
for ln in open(r"D:\LegendOfMortal Wiki\data\alias_pairs.txt", encoding="utf-8"):
    ln = ln.strip()
    if not ln or ln.startswith("#"):
        continue
    a, b = [x.strip() for x in ln.split("=")]
    pairs.append((a, b))
for a, b in pairs:
    sa = {r[0] for r in c.execute("select distinct script from lines where text like ?", ("%" + a + "%",))}
    sb = {r[0] for r in c.execute("select distinct script from lines where text like ?", ("%" + b + "%",))}
    both = sorted(sa & sb)
    print("\n%s = %s  |  %s 独有 %d 场 / %s 独有 %d 场 / 共现 %d 场"
          % (a, b, a, len(sa - sb), b, len(sb - sa), len(both)))
    for sc in both[:2]:
        r = c.execute("""select script,seq,speaker,text from lines where script=? and text like ?
                         order by seq limit 1""", (sc, "%" + a + "%")).fetchone()
        if r:
            print("   共现例 [%s#%s %s] %s" % (r[0], r[1], r[2], r[3][:90].replace("\n", " ")))
