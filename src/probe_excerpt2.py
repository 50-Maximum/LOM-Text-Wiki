# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for t in ("势力", "地点"):
    print(t, "有原文摘录:", c.execute(
        "select count(*) from pages where slug like ? and sections like '%原文摘录%'",
        (t + "/%",)).fetchone()[0])
print("地点占位导语:", c.execute(
    "select count(*) from pages where slug like '地点/%' and lead like '%原文中出现%'").fetchone()[0])
