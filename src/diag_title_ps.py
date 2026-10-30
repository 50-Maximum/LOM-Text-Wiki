# -*- coding: utf-8 -*-
"""看场景页名字是否用了覆盖标题；并打印 placeset 附近代码。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row
r = con.execute("select slug,name,title from pages where slug=?",
                ("场景/S2901_04_02_break_start_01",)).fetchone()
print("场景页:", dict(r) if r else "无")

for i, line in enumerate(open(r"D:\LegendOfMortal Wiki\src\build_wiki2.py", encoding="utf-8"), 1):
    if 690 <= i <= 700:
        print("%4d: %s" % (i, line.rstrip()))
