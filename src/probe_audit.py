# -*- coding: utf-8 -*-
"""站点体检：空页、重复名、疑似错类、无链接的孤儿页。"""
import io, sys, sqlite3, json, collections, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

tot = c.execute("select count(*) from pages").fetchone()[0]
print("页面总数:", tot)

# 空导语
no_lead = c.execute("select count(*) from pages where lead is null or lead=''").fetchone()[0]
print("无导语:", no_lead)

# 同名不同 slug
dup = c.execute("""select name,count(*) c,group_concat(slug,'|') from pages
                   group by name having c>1 order by c desc limit 15""").fetchall()
print("\n同名多页:", len(c.execute("select name from pages group by name having count(*)>1").fetchall()))
for nm, n, slugs in dup[:10]:
    print("   %-12s x%d  %s" % (nm, n, slugs[:80]))

# 势力页里像人名/招式名的
fac = [r[0] for r in c.execute("select name from pages where slug like '势力/%'")]
print("\n势力页:", len(fac))
print("   样例:", fac[:12])

# 孤儿页（无链入）
orph = c.execute("""select p.slug,p.name from pages p
                    where not exists(select 1 from links l where l.dst=p.slug)
                    limit 12""").fetchall()
print("\n无链入页:", c.execute("""select count(*) from pages p
       where not exists(select 1 from links l where l.dst=p.slug)""").fetchone()[0])
for s, n in orph:
    print("   ", s, n)

# 链接指向不存在的页
bad = c.execute("""select l.dst,count(*) from links l
   where not exists(select 1 from pages p where p.slug=l.dst)
   group by l.dst order by 2 desc limit 12""").fetchall()
print("\n坏链目标:", len(c.execute("""select distinct l.dst from links l
   where not exists(select 1 from pages p where p.slug=l.dst)""").fetchall()))
for d, n in bad[:10]:
    print("   %-24s x%d" % (d, n))
