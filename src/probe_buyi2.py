# -*- coding: utf-8 -*-
"""唐布衣续查：卧云岗、与石公远的关系、生死分支。"""
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

show("提到卧云岗", """select script,seq,speaker,text from lines where text like '%卧云岗%'
                      order by script,seq limit 10""")
show("石公远 与 唐布衣/大师兄", """select script,seq,speaker,text from lines
     where text like '%石公远%' and (text like '%大师兄%' or text like '%布衣%')
     order by script,seq limit 10""")
show("大师兄 死/丧/灵堂/遗体", """select script,seq,speaker,text from lines
     where (text like '%大师兄%') and (text like '%灵堂%' or text like '%遗body%'
       or text like '%遗体%' or text like '%丧命%' or text like '%死了%')
     order by script,seq limit 12""")
show("唐布衣 诈死/装死/尸", """select script,seq,speaker,text from lines
     where text like '%唐布衣%' and (text like '%诈死%' or text like '%装死%' or text like '%没死%')
     order by script,seq limit 8""")
