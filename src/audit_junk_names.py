# -*- coding: utf-8 -*-
"""统计：格式串垃圾名、无说明页面、天赋导语形态。"""
import io, sys, json, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

print("=== 名称里带格式串的页面")
rows = c.execute("""select slug,type,name from pages
                    where name like '%{%' or name like '%}%' or name like '%0:0%'""").fetchall()
print(" 共 %d 个" % len(rows))
for r in rows[:15]:
    print("  ", r[0])

print("\n=== 无说明（提示语）页面按类型")
for t, n in c.execute("""select type,count(*) from pages where lead like '%游戏内无说明%'
                         group by type order by 2 desc"""):
    print("  %-8s %d" % (t, n))

print("\n=== 天赋导语以 [ 开头")
n = c.execute("select count(*) from pages where type='天赋' and lead like '[%'").fetchone()[0]
print("  %d" % n)
for r in c.execute("""select name,lead,sections from pages where type='天赋' limit 2"""):
    print("  ", r[0], "|", r[1], "|", r[2][:150])

print("\n=== entries 里 body 是否还有其他字段（松风剑法 / 唐门改良金创药）")
for r in c.execute("""select ns,eid,title,length(body),substr(body,1,120) from entries
                      where title in ('松风剑法','唐门改良金创药','公子侠','爆气')"""):
    print("  ", r)
