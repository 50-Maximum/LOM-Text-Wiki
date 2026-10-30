# -*- coding: utf-8 -*-
"""看库结构：选项存哪张表；顺带列出含「卧云岗」的场景。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for r in c.execute("select name from sqlite_master where type='table'"):
    cols = [x[1] for x in c.execute("pragma table_info(%s)" % r[0])]
    print("%-16s %s" % (r[0], ",".join(cols)))
