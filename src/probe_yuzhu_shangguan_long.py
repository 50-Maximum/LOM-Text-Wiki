# -*- coding: utf-8 -*-
"""郁竹 / 上官萤 / 龙湘 取句。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def show(label, sql, args=(), lim=10):
    print("\n=== " + label)
    rows = list(c.execute(sql, args))[:lim]
    if not rows:
        print("  （无）")
    for r in rows:
        print("  " + " ｜ ".join(str(x).replace("\n", " ")[:76] for x in r))

show("郁竹 铸造/剑/甲", """select script,seq,speaker,text from lines
    where speaker='郁竹' and (text like '%铸%' or text like '%剑%' or text like '%甲%' or text like '%铁%')
    order by script,seq limit 10""")
show("郁竹 门派/身份", """select script,seq,speaker,text from lines
    where text like '%郁竹%' and (text like '%铁拳%' or text like '%崆峒%' or text like '%裂骨%')
    limit 8""")
show("小竹的愿望/学读书烧菜", """select script,seq,speaker,text from lines
    where text like '%读书%' or text like '%烧菜%' limit 8""")

show("上官萤 婚约/北条/东瀛", """select script,seq,speaker,text from lines
    where text like '%上官萤%' and (text like '%婚%' or text like '%北条%' or text like '%东瀛%'
      or text like '%日本%')
    order by script,seq limit 10""")
show("上官萤 出钱/商", """select script,seq,speaker,text from lines
    where speaker='上官萤' and (text like '%银%' or text like '%商%' or text like '%买卖%' or text like '%债%')
    order by script,seq limit 8""")

show("龙湘 锦香宫/惜花令", """select script,seq,speaker,text from lines
    where speaker='龙湘' and (text like '%锦香宫%' or text like '%惜花令%' or text like '%温夫人%')
    order by script,seq limit 8""")
show("龙湘 龙渊之女", """select script,seq,speaker,text from lines
    where text like '%龙渊%' and (text like '%女儿%' or text like '%闺女%' or text like '%父女%')
    limit 8""")
