# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("场景页含本场判定:", c.execute("select count(*) from pages where slug like '场景/%' and sections like '%本场判定%'").fetchone()[0])
print("事件页含触发条件:", c.execute("select count(*) from pages where slug like '事件/%' and sections like '%触发条件%'").fetchone()[0])
for slug in ("场景/S0003_01",):
    r = c.execute("select sections from pages where slug=?", (slug,)).fetchone()
    print(slug, "有本场判定:", "本场判定" in (r[0] if r else ""))
