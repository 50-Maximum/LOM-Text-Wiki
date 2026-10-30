# -*- coding: utf-8 -*-
"""唐升 考据材料：代掌门身份、执法、与唐铮的分歧、结局。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def show(label, sql, args=(), lim=12):
    print("\n=== " + label)
    rows = list(c.execute(sql, args))[:lim]
    if not rows:
        print("  （无）")
    for r in rows:
        print("  " + " ｜ ".join(str(x).replace("\n", " ")[:72] for x in r))

show("唐升 自称代掌门/掌门相关", """select script,seq,speaker,text from lines
    where speaker='唐升' and (text like '%代掌门%' or text like '%掌门%')
    order by script,seq limit 12""")
show("唐升 最关键的自述（判定/法度）", """select script,seq,speaker,text from lines
    where speaker='唐升' and (text like '%本门%' or text like '%法度%' or text like '%门规%')
    order by script,seq limit 10""")
show("他被称作唐三侠", """select script,seq,speaker,text from lines
    where text like '%唐三侠%' limit 8""")
show("唐升 结局相关（战死/死）", """select script,seq,speaker,text from lines
    where text like '%唐升%' and (text like '%死%' or text like '%尸%' or text like '%战%')
    order by script,seq limit 10""")
