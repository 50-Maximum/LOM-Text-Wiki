# -*- coding: utf-8 -*-
"""核对唐中翎三处存疑：①叶氏兄妹是否真的拜入唐门；②许大鲸是否改名唐大鲸；③虞小梅是否已拜师。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def show(label, sql, args=()):
    print("\n=== " + label)
    for sc, seq, sp, tx in c.execute(sql, args):
        print("  %-22s %-4s %-8s %s" % (sc, seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:78]))

show("① S0028_02 里提到拜入/收留的句子",
     """select script,seq,speaker,text from lines where script='S0028_02'
        and (text like '%拜入%' or text like '%收留%' or text like '%唐门弟子%' or text like '%入我唐门%')
        order by seq""")
show("② 唐大鲸 / 许大鲸",
     """select script,seq,speaker,text from lines
        where text like '%大鲸%' and (text like '%改%' or text like '%名%' or text like '%许%')
        order by script,seq limit 12""")
show("③ S2300_01 拜师相关",
     """select script,seq,speaker,text from lines where script='S2300_01'
        and (text like '%拜师%' or text like '%弟子%') order by seq""")
show("④ 虞小梅 门派归属（崆峒/飞天）",
     """select script,seq,speaker,text from lines
        where text like '%小梅%' and (text like '%崆峒%' or text like '%飞天%')
        order by script,seq limit 12""")
