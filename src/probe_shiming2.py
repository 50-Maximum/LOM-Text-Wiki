# -*- coding: utf-8 -*-
"""释明＝无相祖师 的线索排查（分句、分场景、事件名三条路）。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def show(label, sql, args=(), lim=12):
    print("\n=== " + label)
    rows = list(c.execute(sql, args))[:lim]
    if not rows:
        print("  （无）")
    for r in rows:
        print("  " + " ｜ ".join(str(x).replace("\n", " ")[:70] for x in r))

show("老和尚 + 无相/千面/人魔",
     """select script,seq,speaker,text from lines
        where text like '%老和尚%' and (text like '%无相%' or text like '%千面%' or text like '%人魔%')
        order by script,seq""")
show("无相祖师/千面人魔 出现在哪些场景（按句数）",
     """select script,count(*) from lines
        where text like '%无相祖师%' or text like '%千面人魔%'
        group by script order by 2 desc""")
show("释明 出场的场景（按句数）",
     """select script,count(*) from lines where speaker='释明' group by script order by 2 desc""")
show("同时有释明与无相的脚本",
     """select script from lines where speaker='释明' group by script
        intersect
        select script from lines where text like '%无相%' group by script""")
