# -*- coding: utf-8 -*-
"""夏侯兰 / 叶云舟 考据取句：身份、收徒、传功、下山、与唐门的关系。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def show(label, sql, args=(), lim=12):
    print("\n=== " + label)
    rows = list(c.execute(sql, args))[:lim]
    if not rows:
        print("  （无）")
    for r in rows:
        print("  " + " ｜ ".join(str(x).replace("\n", " ")[:74] for x in r))

# ---- 夏侯兰 ----
show("夏侯兰 自称/门派", """select script,seq,speaker,text from lines where speaker='夏侯兰'
    and (text like '%雪山%' or text like '%师父%' or text like '%为师%' or text like '%本座%')
    order by script,seq limit 12""")
show("收赵活为徒", """select script,seq,speaker,text from lines
    where text like '%夏侯兰%' and (text like '%收%徒%' or text like '%拜师%' or text like '%弟子%')
    order by script,seq limit 10""")
show("传功/散功/死", """select script,seq,speaker,text from lines where speaker='夏侯兰'
    and (text like '%传功%' or text like '%散功%' or text like '%内力%' or text like '%死%')
    order by script,seq limit 12""")
show("夺魄幽兰 / 雪山派 称谓", """select script,seq,speaker,text from lines
    where text like '%夺魄幽兰%' or text like '%雪山派%' limit 10""")

# ---- 叶云舟 ----
show("叶云舟 自称点苍/剑", """select script,seq,speaker,text from lines where speaker='叶云舟'
    and (text like '%点苍%' or text like '%剑%' or text like '%云裳%')
    order by script,seq limit 12""")
show("点苍剑鬼 称谓", """select script,seq,speaker,text from lines where text like '%点苍剑鬼%' limit 8""")
show("叶云舟 入唐门/代表唐门", """select script,seq,speaker,text from lines
    where text like '%叶云舟%' and (text like '%唐门%' or text like '%入%')
    order by script,seq limit 10""")
show("独自离开/离唐门", """select script,seq,speaker,text from lines
    where text like '%叶%' and (text like '%离开唐门%' or text like '%不告而别%' or text like '%走了%')
    order by script,seq limit 10""")
