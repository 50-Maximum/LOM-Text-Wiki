# -*- coding: utf-8 -*-
import sqlite3, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("===== ch8_8_1 全部尾声块（条件+样例） =====")
rows = c.execute("select chain,n,seq,substr(text,1,60) from endings where script='ch8_8_1' order by n").fetchall()
for r in rows:
    chain = " | ".join(json.loads(r[0]))[:150]
    print(f"块n={r[1]} seq={r[2]} 条件[{chain}] {r[3]}")

print("\n===== ch8 里云舟/云裳出现的其他场景 =====")
for r in c.execute("""select script,count(*) from lines
                      where script like 'ch8%' and (text like '%云舟%' or text like '%云裳%')
                      group by script"""):
    print(r)
