# -*- coding: utf-8 -*-
import sqlite3, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

for slug in ("势力/泥教", "世界观/总览", "人物/赵活", "人物/叶云裳", "人物/唐升", "人物/南宫深"):
    r = c.execute("select slug,type,name,lead,sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        print(slug, "不存在"); continue
    secs = json.loads(r[4])
    print(f"\n===== {slug} =====")
    print(r[3][:130])
    for s in secs:
        if s["h"] == "脚注":
            for row in s["rows"]:
                print(f"  脚注: {row['note'][:60]} | {row['quote'][:30]}")
        elif s.get("html"):
            print(f"  [{s['h']}] {s['html'][:80]}")

print("\n===== S0003_02_06_03 事件 ====")
for r in c.execute("select name,quote from notes where script='S0003_02_06_03' and type='事件'"):
    print(r)
