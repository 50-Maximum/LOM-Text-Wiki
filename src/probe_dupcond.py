# -*- coding: utf-8 -*-
import io, sys, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
rows = c.execute("""select slug, sections from pages
                    where slug like '事件/%' and sections like '%触发条件%'
                    order by length(sections) desc limit 3""").fetchall()
for slug, sec in rows:
    S = json.loads(sec)
    print("\n==", slug)
    for s in S:
        if s.get("h") == "触发条件":
            notes = [r.get("note", "") for r in s["rows"]]
            print("   行数 %d，重复 %d" % (len(notes), len(notes) - len(set(notes))))
            for n in notes[:8]:
                print("     -", n[:80])
