# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for t in ("装备", "物品", "天赋", "武学", "成就", "战斗效果", "设施", "战技", "关系"):
    n = c.execute("select count(*) from pages where type=? and hidden=0 and length(lead)<12", (t,)).fetchone()[0]
    print("%-5s 薄导语 %d" % (t, n))
    for nm, ld in c.execute("select name,lead from pages where type=? and hidden=0 and length(lead)<12 limit 3", (t,)):
        print("     ", nm, "|", (ld or "")[:60])
