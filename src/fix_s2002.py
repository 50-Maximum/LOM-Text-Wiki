# -*- coding: utf-8 -*-
"""S2002 组按旗标与攻略窗口归段：上官萤拜访唐门一线。
证据：
  S2002_01 条件 书籍_全真剑法≥1／嘴力≥30
  S2002_02 需要 G10001〔已经认识上官萤〕=1 且 上官萤好感≥10
  S2002_04 置 G10001（即首次拜访=认识上官萤），条件 性情≤40／学问≥45／嘴力≥45
  攻略「假字据」窗口：第一年八月中旬到第二年七月上旬，🚩上官萤在唐门
  负债条件（门派资产<-9000/-6000）在 S2914_01，不在 S2002
"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
p = os.path.join(B, "arcs.json")
d = json.load(open(p, encoding="utf-8"))
sc = d.setdefault("scene", {})
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
names = [r["script"] for r in c.execute("select script from scenes where script like 'S2002%'")]
for n in names:
    sc[n] = "外姓弟子"
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("S2002 组 %d 场 → 外姓弟子" % len(names))
for n in names:
    print("   ", n)
