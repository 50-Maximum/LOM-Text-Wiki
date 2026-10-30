# -*- coding: utf-8 -*-
"""找全真相关条目名。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
for pat in ("%全真%", "%重阳%", "%终南%"):
    print("== ", pat)
    for r in con.execute("select slug,name,type from pages where name like ? or slug like ? limit 20",
                         (pat, pat)):
        print("   ", r)
