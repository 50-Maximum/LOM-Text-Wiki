# -*- coding: utf-8 -*-
"""找「娘喊吃饭」那组梦境场景，以及其他梦境场景。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

print("=== 台词同时含「娘」与「吃饭/吃饭」的场景")
for sc, n in c.execute("""select script,count(*) from lines
    where text like '%娘%' and (text like '%吃饭%' or text like '%用膳%' or text like '%开饭%')
    group by script order by 2 desc limit 10"""):
    t = c.execute("select title from scenes where script=?", (sc,)).fetchone()
    print("  %-24s %2d 句 ｜ %s" % (sc, n, (t[0] if t else "")[:30]))

print("\n=== 标题含梦/梦回/作梦 的场景")
for sc, t in c.execute("""select script,title from scenes
    where title like '%梦%' order by script limit 20"""):
    print("  %-24s %s" % (sc, (t or "")[:34]))

print("\n=== S8500_01 系列")
for sc, seq, sp, tx in c.execute("""select script,seq,speaker,text from lines
    where script like 'S8500_01%' order by script,seq limit 24"""):
    print("  %-18s %-4s %-8s %s" % (sc, seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:70]))
