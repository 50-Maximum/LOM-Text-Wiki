# -*- coding: utf-8 -*-
import sqlite3, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("===== endings 表结构 =====")
print([r[1] for r in c.execute("pragma table_info(endings)")])
print("\n===== endings 提及 云裳/梁有诗/云舟 =====")
for r in c.execute("""select * from endings where text like '%云裳%' or text like '%梁有诗%' or text like '%云舟%' limit 25"""):
    print(r)

print("\n===== 赵活接唐门掌门 证据 =====")
for r in c.execute("""select script,seq_from,name,note,quote from notes
                      where (note like '%赵活%' and note like '%掌门%') or note like '%接任掌门%' or note like '%新掌门%赵%'
                      order by script,seq_from limit 20"""):
    print(f"{r[0]}#{r[1]} [{r[2]}] {r[3][:60]} | {r[4][:34]}")
