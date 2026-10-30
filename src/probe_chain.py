# -*- coding: utf-8 -*-
import io, sys, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
n = c.execute("select count(*) from pages where sections like '%剧情衔接%'").fetchone()[0]
print("有剧情衔接段的页:", n)
rows = c.execute("""select slug,sections from pages where slug like '事件/%'
                    and sections like '%剧情衔接%' limit 2""").fetchall()
for slug, sec in rows:
    print("\n==", slug)
    for s in json.loads(sec):
        if s.get("h") == "剧情衔接":
            for r in s["rows"][:6]:
                print("   ", r["note"][:60], "→", r["script"])
