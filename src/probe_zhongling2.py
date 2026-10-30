# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def show(label, sql, args=()):
    print("\n=== " + label)
    for sc, seq, sp, tx in c.execute(sql, args):
        print("  %-16s %-4s %-8s %s" % (sc, seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:80]))

show("ch1_1_2 传位/许配",
     """select script,seq,speaker,text from lines where script='ch1_1_2'
        and (text like '%掌门之位%' or text like '%传予%' or text like '%铃儿%' or text like '%许配%'
             or text like '%婚%' or text like '%德行%' or text like '%暂%') order by seq""")
show("ch8_2_5_7 释明",
     """select script,seq,speaker,text from lines where script='ch8_2_5_7'
        and (text like '%唐中翎%' or text like '%掐死%' or text like '%心魔%') order by seq limit 8""")
show("老魔 旧闻",
     """select script,seq,speaker,text from lines
        where text like '%老魔%' order by script,seq limit 6""")
