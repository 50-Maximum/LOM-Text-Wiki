# -*- coding: utf-8 -*-
import sqlite3, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
for slug in ("地点/眉山", "地点/唐门", "地点/崆峒山"):
    r = c.execute("select lead,sections from pages where slug=?", (slug,)).fetchone()
    print(f"\n===== {slug} =====")
    print("lead:", r[0])
    for s in json.loads(r[1]):
        print(" [", s["h"], "]", json.dumps(s, ensure_ascii=False)[:500])
