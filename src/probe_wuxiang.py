# -*- coding: utf-8 -*-
"""唐铮与无相祖师：找出相关场景与原文。"""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== 提到「无相祖师」的场景 ==")
for sc, ti, n in c.execute("""select l.script, s.title, count(*) from lines l
                              left join scenes s on s.script=l.script
                              where l.text like '%无相祖师%' or l.text like '%无相%'
                              group by l.script order by 3 desc limit 20"""):
    print(f"  {sc:26} {n:3}  {ti}")

print("\n== 这些场景里含「唐铮」的句子 ==")
for sc, ti in c.execute("""select distinct l.script,s.title from lines l
                           left join scenes s on s.script=l.script
                           where (l.text like '%无相祖师%' or l.text like '%无相%')"""):
    rows = c.execute("""select seq,speaker,text from lines where script=?
                        and (text like '%唐铮%' or speaker='唐铮') order by seq""", (sc,)).fetchall()
    if rows:
        print(f"\n-- {sc} 《{ti}》")
        for r in rows[:20]:
            print(f"   {r[0]:3} {r[1]}：{(r[2] or '')[:90]}")

print("\n== 全库「唐铮」说自己属唐门/心属唐门 ==")
for r in c.execute("""select script,seq,speaker,text from lines
                      where (text like '%心属唐门%' or text like '%我属唐门%'
                             or text like '%我是唐门%' or text like '%此生%唐门%')
                      and (speaker='唐铮' or text like '%唐铮%') limit 20"""):
    print("  ", r[0], r[1], r[2], "：", (r[3] or "")[:90])
