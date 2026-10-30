# -*- coding: utf-8 -*-
"""核对：老和尚释明是否就是无相祖师；唐铮、唐布衣与他的交手在哪几场。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def show(label, sql, args=(), lim=12):
    print("\n=== " + label)
    rows = list(c.execute(sql, args))[:lim]
    if not rows:
        print("  （无）")
    for sc, seq, sp, tx in rows:
        print("  %-26s %-4s %-8s %s" % (sc, seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:76]))

show("释明 与 无相/千面 同句", """select script,seq,speaker,text from lines
    where text like '%释明%' and (text like '%无相%' or text like '%千面%')
    order by script,seq""")
show("释明 出场最多的场景", """select script,count(*) n,min(speaker) from lines
    where speaker='释明' group by script order by n desc limit 8""")
show("唐铮 + 释明 同场", """select l1.script,count(*) n,min(l1.speaker) from lines l1
    where l1.script in (select script from lines where speaker='释明')
      and l1.script in (select script from lines where speaker='唐铮')
    group by l1.script order by n desc limit 8""")
show("毒 + 祖师/和尚 的旁白", """select script,seq,speaker,text from lines
    where (text like '%毒倒%' or text like '%中毒%') and (text like '%祖师%' or text like '%老和尚%')
    order by script,seq limit 10""")
