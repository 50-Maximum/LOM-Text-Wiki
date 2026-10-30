# -*- coding: utf-8 -*-
"""看崆峒山下有哪些子地点页，决定可以用哪些全名。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
print("--- 名称含崆峒 ---")
for r in c.execute("select slug,name,type from pages where name like '%崆峒%' order by name"):
    print("   %-28s %-10s %s" % (r[0], r[2], r[1]))
print("--- 名称含夺魄/铁拳/玄功/飞天殿/无色 ---")
for r in c.execute("select slug,name,type from pages where name like '%夺魄%' or name like '%铁拳%' "
                   "or name like '%玄功%' or name like '%飞天殿%' or name like '%无色%' order by name"):
    print("   %-28s %-10s %s" % (r[0], r[2], r[1]))
