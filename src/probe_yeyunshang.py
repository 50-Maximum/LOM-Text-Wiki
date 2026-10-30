# -*- coding: utf-8 -*-
"""叶云裳取句：身世、混世魔王、义兄妹、病情、幽泉附身。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def show(label, sql, args=(), lim=12):
    print("\n=== " + label)
    rows = list(c.execute(sql, args))[:lim]
    if not rows:
        print("  （无）")
    for r in rows:
        print("  " + " ｜ ".join(str(x).replace("\n", " ")[:78] for x in r))

show("混世魔王", """select script,seq,speaker,text from lines where text like '%混世魔王%' limit 8""")
show("义兄妹/义兄", """select script,seq,speaker,text from lines
    where (text like '%义兄妹%' or text like '%义兄%') order by script,seq limit 10""")
show("叶云裳 自述身世/病", """select script,seq,speaker,text from lines where speaker='叶云裳'
    and (text like '%爹%' or text like '%娘%' or text like '%病%' or text like '%毒%' or text like '%死%')
    order by script,seq limit 12""")
show("幽泉附身", """select script,seq,speaker,text from lines
    where text like '%幽泉%' order by script,seq limit 10""")
