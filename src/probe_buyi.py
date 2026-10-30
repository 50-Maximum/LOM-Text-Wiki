# -*- coding: utf-8 -*-
"""核对唐布衣旧稿四处：卧云岗与石公远决战／飞燕流星翎封穴／与金乌上人伤重／退隐说相声。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def show(label, sql, args=()):
    print("\n=== " + label)
    for sc, seq, sp, tx in c.execute(sql, args):
        print("  %-24s %-4s %-8s %s" % (sc, seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:76]))

show("石公远 + 卧云岗/决战",
     """select script,seq,speaker,text from lines
        where text like '%石公远%' and (text like '%决战%' or text like '%卧云%' or text like '%约战%')
        order by script,seq limit 10""")
show("飞燕流星翎",
     """select script,seq,speaker,text from lines where text like '%飞燕流星翎%'
        order by script,seq limit 10""")
show("金乌上人 + 唐布衣 伤",
     """select script,seq,speaker,text from lines
        where text like '%金乌%' and (text like '%大师兄%' or text like '%唐布衣%')
        order by script,seq limit 10""")
show("说相声 / 退隐",
     """select script,seq,speaker,text from lines
        where (text like '%相声%' or text like '%退隐%') and speaker='唐布衣'
        order by script,seq limit 10""")
