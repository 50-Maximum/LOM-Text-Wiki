# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

keys = ["南宫", "寿宴", "江陵", "围城", "招亲", "选婿", "武林大会", "风雨山", "檄文", "围攻", "唐门血战", "留学", "青城", "崆峒"]
for k in keys:
    print(f"\n===== {k} =====")
    for r in c.execute("""select year,month,xun,name,scripts from guide_index
                          where name like ? or body like ? order by year,month limit 8""",
                       (f"%{k}%", f"%{k}%")):
        print(f"{r[0]}年{r[1]}月{r[2] or ''} [{r[3]}] {r[4][:50]}")

print("\n===== guide_events 时间全表（主线） =====")
for r in c.execute("select year,month,xun,name,cond from guide_events order by year,month"):
    print(f"{r[0]}年{r[1]}月{r[2] or ''} {r[3]} ｜ {r[4][:40]}")
