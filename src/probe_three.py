# -*- coding: utf-8 -*-
"""查三件事：①南沟残留页来源；②金乌势力；③谷底相关场景。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

print("=== ① 南沟 ===")
for r in c.execute("select slug,lead,sections,mentions from pages where name in ('南沟','南沟集')"):
    secs = json.loads(r["sections"] or "[]")
    print("  %-14s mentions=%s sections=%s" % (r["slug"], r["mentions"], [s.get("h") for s in secs]))
for r in c.execute("select place,count(*) n from scenes where place like '%南沟%' group by place"):
    print("  scenes.place:", r["place"], r["n"])

print("\n=== ② 金乌 ===")
for r in c.execute("select slug,name,type from pages where name like '%金乌%' or slug like '%金乌%'"):
    print("  ", r["slug"], r["type"], r["name"])

print("\n=== ③ 谷底 / 叶云裳 跌落 ===")
seen = set()
for r in c.execute("""select script, seq, text from lines
                      where text like '%谷底%' or (text like '%跌落%' and text like '%云裳%')"""):
    if r["script"] in seen:
        continue
    seen.add(r["script"])
    sc = c.execute("select title,chapter,place from scenes where script=?", (r["script"],)).fetchone()
    print("  %-18s %-16s place=%-10s #%d %s" % (r["script"], (sc["title"] if sc else "") or "",
                                                (sc["place"] if sc else "") or "", r["seq"],
                                                (r["text"] or "")[:60]))
    if len(seen) >= 12:
        break
