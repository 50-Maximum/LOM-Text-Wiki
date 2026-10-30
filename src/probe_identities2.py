# -*- coding: utf-8 -*-
"""继续排查：释明与无相祖师的关系；画中仙与千面人魔的关系；老和尚出现在哪些场。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def show(label, sql, args=(), lim=14):
    print("\n=== " + label)
    rows = list(c.execute(sql, args))[:lim]
    if not rows:
        print("  （无）")
    for r in rows:
        print("  " + " ｜ ".join(str(x).replace("\n", " ")[:74] for x in r))

show("释明 的自我表明/身份相关",
     """select script,seq,speaker,text from lines where speaker='释明'
        and (text like '%千灯%' or text like '%极乐%' or text like '%易容%' or text like '%本座%'
          or text like '%老衲%' or text like '%无相%' or text like '%画皮%')
        order by script,seq limit 14""")
show("老和尚 出现场景",
     """select script,count(*) from lines where speaker='老和尚' group by script order by 2 desc""")
show("画中仙 与 千面 的句子",
     """select script,seq,speaker,text from lines where text like '%画中仙%'
        order by script,seq limit 14""")
show("谁被称为千面人魔（同句）",
     """select script,seq,speaker,text from lines where text like '%千面人魔%'
        and (text like '%是%' or text like '%正是%') order by script,seq limit 14""")
