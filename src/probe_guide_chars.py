# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

for kw in ("唐升", "叶云裳", "龙湘", "上官萤", "唐默铃"):
    print(f"\n########## {kw} ##########")
    rows = c.execute("""select year,month,xun,name,substr(body,1,700) from guide_events
                        where body like ? order by year,month limit 12""", (f"%{kw}%",)).fetchall()
    for r in rows:
        print(f"--- {r[0]}年{r[1]}月{r[2] or ''} [{r[3]}]")
        print(r[4].replace("\n", " ")[:600])
