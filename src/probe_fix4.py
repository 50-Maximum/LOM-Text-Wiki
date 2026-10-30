# -*- coding: utf-8 -*-
"""补查：①赵活试穿虎甲太重 ②丹霞子在外堡的戏 ③丹霞子立场。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def show(label, sql, args=(), lim=14):
    print("\n=== " + label)
    rows = list(c.execute(sql, args))[:lim]
    if not rows:
        print("  （无）")
    for r in rows:
        print("  " + " ｜ ".join(str(x).replace("\n", " ")[:80] for x in r))

show("虎甲太重／钢铁", """select script,seq,speaker,text from lines
    where (text like '%甲%' and (text like '%太重%' or text like '%钢铁%' or text like '%穿不动%'
      or text like '%机关甲%' or text like '%量身%'))
    order by script,seq limit 12""")
show("赵活 + 老虎", """select script,seq,speaker,text from lines
    where text like '%老虎%' order by script,seq limit 12""")
show("丹霞子在哪些场景（按句数）", """select script,count(*) from lines where speaker='丹霞子'
    group by script order by 2 desc limit 12""")
show("外堡战 / 外堡 攻", """select script,seq,speaker,text from lines
    where text like '%外堡%' and (text like '%攻%' or text like '%战%' or text like '%守%')
    order by script,seq limit 12""")
