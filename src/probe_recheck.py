# -*- coding: utf-8 -*-
"""复查我此前判定「查无此说」的三处，改用别名与场景检索。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def show(label, sql, args=(), lim=14):
    print("\n=== " + label)
    rows = list(c.execute(sql, args))[:lim]
    if not rows:
        print("  （无）")
    for r in rows:
        print("  " + " ｜ ".join(str(x).replace("\n", " ")[:72] for x in r))

show("A 叶氏兄妹 拜入/投入唐门",
     """select script,seq,speaker,text from lines
        where text like '%拜入唐门%' or text like '%投入唐门%' or text like '%入我唐门%'
           or text like '%收你们入%' or text like '%收你为徒%'
        order by script,seq""")
show("B 卧云岗 封穴/点穴/假死/佯",
     """select script,seq,speaker,text from lines
        where (text like '%封穴%' or text like '%点穴%' or text like '%假死%' or text like '%佯%')
          and (text like '%石公远%' or text like '%石帮主%' or text like '%卧云%')
        order by script,seq""")
show("C 掌派人之战 结果",
     """select script,seq,speaker,text from lines
        where text like '%掌派人之战%' or (text like '%金乌%' and text like '%掌派人%')
        order by script,seq limit 14""")
show("D 唐布衣 伤/输 与 金乌",
     """select script,seq,speaker,text from lines
        where text like '%金乌%' and (text like '%伤了%' or text like '%重伤%' or text like '%吐血%'
          or text like '%败%' or text like '%输%')
        order by script,seq limit 14""")
