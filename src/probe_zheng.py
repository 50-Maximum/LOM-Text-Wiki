# -*- coding: utf-8 -*-
"""核对唐铮旧稿的「三重卧底」与「毒倒无相祖师」。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def show(label, sql, args=()):
    print("\n=== " + label)
    rows = list(c.execute(sql, args))
    if not rows:
        print("  （无）")
    for sc, seq, sp, tx in rows:
        print("  %-26s %-4s %-8s %s" % (sc, seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:74]))

show("唐铮 + 千灯楼", """select script,seq,speaker,text from lines
    where text like '%唐铮%' and text like '%千灯楼%' order by script,seq limit 10""")
show("唐铮 + 锦香宫", """select script,seq,speaker,text from lines
    where text like '%唐铮%' and text like '%锦香宫%' order by script,seq limit 10""")
show("无相祖师 + 毒/唐铮", """select script,seq,speaker,text from lines
    where text like '%无相祖师%' order by script,seq limit 10""")
show("唐铮 自陈身份（卧底）", """select script,seq,speaker,text from lines
    where speaker='唐铮' and (text like '%卧底%' or text like '%潜伏%' or text like '%细作%')
    order by script,seq limit 10""")
