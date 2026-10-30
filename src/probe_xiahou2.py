# -*- coding: utf-8 -*-
"""夏侯兰：门派到底写崆峒还是雪山；她是否真的传功而死。"""
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

show("夏侯兰 + 雪山", """select script,seq,speaker,text from lines
    where text like '%夏侯兰%' and text like '%雪山%' order by script,seq limit 10""")
show("夏侯兰 死/咽气/坟", """select script,seq,speaker,text from lines
    where text like '%夏侯兰%' and (text like '%死了%' or text like '%气绝%' or text like '%遗体%'
      or text like '%坟%' or text like '%墓碑%')
    order by script,seq limit 10""")
show("散功/传功 与 夏侯兰 同场", """select script,seq,speaker,text from lines
    where (text like '%散功%' or text like '%传功%') and text like '%夏侯%'
    order by script,seq limit 8""")
show("雪山派 弟子 赵活", """select script,seq,speaker,text from lines
    where text like '%雪山派%' and text like '%弟子%' limit 10""")
