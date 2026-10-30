# -*- coding: utf-8 -*-
"""看 lines.branch 的形态，决定分支页怎么建。"""
import os, sys, io, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== lines 结构 ==")
cols = [r[1] for r in c.execute("PRAGMA table_info(lines)")]
print("  ", cols)
txtcol = "text" if "text" in cols else cols[3]
print("== 有 branch 的台词:", c.execute("select count(*) from lines where branch<>''").fetchone()[0],
      "/", c.execute("select count(*) from lines").fetchone()[0])

for sid in ("S0017_01", "S0003_01_03", "ch5_3_1"):
    print("\n=== ", sid)
    q = f"select seq,speaker,substr({txtcol},1,30),branch from lines where script=? order by seq"
    for r in c.execute(q, (sid,)):
        if r[3]:
            print(f"  {r[0]:3} {str(r[1])[:6]:6} {r[2]!r}  <<{r[3][:70]}>>")

print("\n=== 分支标签末段 top ===")
cnt = collections.Counter()
for (b,) in c.execute("select distinct branch from lines where branch<>''"):
    cnt[b.split(" > ")[-1][:24]] += 1
for k, v in cnt.most_common(12):
    print(f"  {v:5}  {k}")
