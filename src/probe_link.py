# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("factions 有千灯楼?", c.execute("select name from factions where name like '%千灯%'").fetchall())
print("关系含千灯楼:", c.execute("select name,note from ledger where type='关系' and name like '%千灯%' limit 8").fetchall())
print("tags 含千灯楼的人物:", c.execute("""select name from entities where type='人物' and tags like '%千灯楼%' limit 10""").fetchall())
print("场景含千灯楼台词:", c.execute("""select count(distinct l.script) from lines l where l.text like '%千灯楼%'""").fetchone())
print("唐门大院相关 place:", c.execute("select distinct place from scenes where place like '%大院%' limit 5").fetchall())
print("tags 含唐门大院:", c.execute("""select count(*) from entities where tags like '%大院%'""").fetchone())
