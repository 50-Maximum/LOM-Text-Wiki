# -*- coding: utf-8 -*-
import sqlite3, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== src 文件 ==")
for f in sorted(os.listdir(r"D:\LegendOfMortal Wiki\src")):
    if f.endswith(".py"):
        print("  ", f)

print()
print("== 第5章·2 台账（前 10）==")
for r in c.execute("select type,name,note,evidence from ledger where chapter like '第5章·2%' limit 10"):
    print(f"  {r[0]}｜{r[1]}｜{(r[2] or '')[:70]}｜{((r[3] or '')[:50])}")

print()
print("== 含「招亲」的台账 ==")
for r in c.execute("select chapter,type,name,note,evidence from ledger where note like '%招亲%' limit 8"):
    print(f"  {r[0]}｜{r[1]}｜{r[2][:60]}｜{((r[3] or '')[:50])}")

print()
print("== evidence 为空的比例 ==")
tot = c.execute("select count(*) from ledger").fetchone()[0]
emp = c.execute("select count(*) from ledger where evidence is null or evidence=''").fetchone()[0]
print("   ", emp, "/", tot)
