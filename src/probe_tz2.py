# -*- coding: utf-8 -*-
"""读 ch8_7_2_2_2 唐铮摊牌段，以及找无相祖师之死。"""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== ch8_7_2_2_2 前 70 句 ==")
for r in c.execute("select seq,speaker,text from lines where script='ch8_7_2_2_2' and seq<=70 order by seq"):
    print(f"{r[0]:3} {r[1]}：{(r[2] or '').replace(chr(10),' ')[:110]}")

print("\n== 搜「无相祖师」死/杀 相关 ==")
for r in c.execute("""select script,seq,speaker,text from lines
                      where (text like '%无相祖师%' or text like '%无相%')
                      and (text like '%死%' or text like '%杀%' or text like '%斩%' or text like '%伏%')
                      order by script,seq limit 30"""):
    print(f"  {r[0]}#{r[1]} {r[2]}：{(r[3] or '')[:90]}")
