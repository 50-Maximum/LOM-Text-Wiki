# -*- coding: utf-8 -*-
import io, sys, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
rows = c.execute("""select slug, sections from pages where slug like '场景/%'
                    and sections like '%本场判定%' order by length(sections) desc limit 3""").fetchall()
for slug, sec in rows:
    S = json.loads(sec)
    print("\n==", slug)
    for s in S:
        if s.get("h") == "本场判定":
            notes = [r.get("note", "") for r in s.get("rows") or []]
            print("   行数", len(notes))
            for n in notes[:6]:
                print("     -", n[:90])
