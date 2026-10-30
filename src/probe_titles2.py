# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
print("标题来源分布：")
for r in c.execute("select title_src,count(*) from scenes group by title_src order by 2 desc"):
    print("   ", r)
print()
print("新命名样例（原 50 句以上）：")
for r in c.execute("""select script,title,chapter,line_count from scenes
                      where title_src='llm' order by line_count desc limit 20"""):
    print(f"   {r[1]:<18} [{r[2]}] {r[3]}句  {r[0]}")
