# -*- coding: utf-8 -*-
"""找每条感情线的收尾场景。"""
import sqlite3, sys, io, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== ch8_8 系列场景 ==")
for r in c.execute("""select script,title,line_count from scenes
                      where script like 'ch8_8%' order by script"""):
    print(f"  {r[0]:24} {r[2]:4} {r[1]}")

print("\n== 标题含 愿望/成亲/婚后/归隐/结局/后话 ==")
for r in c.execute("""select script,title,chapter,line_count from scenes
                      where title like '%愿望%' or title like '%成亲%' or title like '%婚后%'
                         or title like '%归隐%' or title like '%结局%' or title like '%后话%'
                      order by script"""):
    print(f"  {r[0]:24} {r[2] or '':6} {r[3]:4} {r[1]}")

print("\n== 各 G11 旗标在第8章要求到的场景 ==")
sf = json.load(open(r"D:\LegendOfMortal Wiki\data\scene_flags.json", encoding="utf-8"))
for g in ("G11000","G11001","G11002","G11003","G11004","G11005","G11006","G11007"):
    hits = []
    for sc, info in sf.items():
        for rq in info.get("requires", []) or []:
            if isinstance(rq, dict) and rq.get("flag") == g:
                row = c.execute("select title,chapter,line_count from scenes where script=?", (sc,)).fetchone()
                if row and row[1] == "第8章":
                    hits.append((sc, row[0], row[2]))
    print(f"\n-- {g} 第8章场景 {len(hits)}")
    for h in hits[:12]:
        print("   ", h)
