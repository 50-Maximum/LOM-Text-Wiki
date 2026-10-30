# -*- coding: utf-8 -*-
import io, sys, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
rows = c.execute("select slug,name,infobox,sections from pages where slug like '事件/%' and infobox like '%推断时间%' limit 4").fetchall()
print("带推断时间的事件页:", c.execute("select count(*) from pages where slug like '事件/%' and infobox like '%推断时间%'").fetchone()[0])
for slug, nm, inf, sec in rows:
    print("\n==", nm)
    print("  ", inf[:150])
    for s in json.loads(sec):
        if s.get("h") == "时间推导":
            print("   [时间推导]", (s.get("html") or "")[:90])
