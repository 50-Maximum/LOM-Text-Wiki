# -*- coding: utf-8 -*-
"""读结局段落：小梅/小竹/大师兄；以及唐铮心属唐门的原句。"""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== ch8_8_1 seq 180-215 ==")
for r in c.execute("select seq,speaker,text from lines where script='ch8_8_1' and seq between 180 and 215 order by seq"):
    print(f"{r[0]:3} {r[1]}：{(r[2] or '').replace(chr(10),' ')[:100]}")

print("\n== ch8_8_1 seq 300-347 ==")
for r in c.execute("select seq,speaker,text from lines where script='ch8_8_1' and seq between 300 and 347 order by seq"):
    print(f"{r[0]:3} {r[1]}：{(r[2] or '').replace(chr(10),' ')[:100]}")

print("\n== 唐铮「心属/唐门人/我是唐门」 ==")
for r in c.execute("""select script,seq,speaker,text from lines
                      where speaker='唐铮' and (text like '%心属%' or text like '%唐门人%'
                      or text like '%我是唐门%' or text like '%我属%') limit 20"""):
    print("  ", r[0], r[1], "：", (r[3] or "")[:90])
