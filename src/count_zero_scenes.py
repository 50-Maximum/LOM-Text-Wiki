# -*- coding: utf-8 -*-
"""统计 0 句场景（转场脚本）数量与是否有标题。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
n0 = c.execute("select count(*) from scenes where line_count=0").fetchone()[0]
n0t = c.execute("select count(*) from scenes where line_count=0 and title is not null").fetchone()[0]
print("0 句场景:", n0, "其中有标题:", n0t)
for r in c.execute("select script,title,chapter from scenes where line_count=0 limit 8"):
    print("   ", r["script"], "|", r["title"], "|", r["chapter"])
print("总场景:", c.execute("select count(*) from scenes").fetchone()[0])
