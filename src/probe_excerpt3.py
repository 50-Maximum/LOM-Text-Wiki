# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("原文摘录页合计:", c.execute("select count(*) from pages where sections like '%原文摘录%'").fetchone()[0])
for pref in ("战斗角色", "战斗效果", "武学", "书物", "物品", "天赋", "设施", "成就"):
    n = c.execute("select count(*) from pages where slug like ? and sections like '%原文摘录%'", (pref + "/%",)).fetchone()[0]
    t = c.execute("select count(*) from pages where slug like ?", (pref + "/%",)).fetchone()[0]
    print("   %-6s %d/%d" % (pref, n, t))
print("仍写无说明的:", c.execute("select count(*) from pages where lead like '%无说明%'").fetchone()[0])
