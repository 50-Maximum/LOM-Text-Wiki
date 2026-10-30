# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
for slug in ("人物/赵活", "人物/唐默铃", "人物/瑞笙", "势力/唐门", "地点/江陵", "结局/终章"):
    r = c.execute("select slug,lead from pages where slug=?", (slug,)).fetchone()
    print((r[0] + " | " + (r[1] or "")[:70]) if r else ("缺 " + slug))
print("总页面", c.execute("select count(*) from pages").fetchone()[0],
      "笔记", c.execute("select count(*) from notes").fetchone()[0],
      "场景", c.execute("select count(distinct script) from notes").fetchone()[0])
