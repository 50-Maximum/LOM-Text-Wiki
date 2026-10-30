# -*- coding: utf-8 -*-
"""对账：台账的章节名 vs 场景的章节名；找招亲场景与留学选择。"""
import sqlite3, sys, io, os, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== 台账章节 TOP ==")
for r in c.execute("select chapter,count(*) from ledger group by chapter order by 2 desc limit 18"):
    print("   ", r)

print()
print("== 场景章节 ==")
for r in c.execute("select chapter,count(*) from scenes group by chapter order by 2 desc"):
    print("   ", r)

print()
print("== 招亲相关场景 ==")
for r in c.execute("select script,title,chapter,line_count from scenes where title like '%招亲%' or title like '%求亲%' order by line_count desc limit 10"):
    print("   ", r)

print()
print("== 含 南宫深 的场景 ==")
for r in c.execute("""select s.script,s.title,s.chapter,count(*) n from lines l
                      join scenes s on s.script=l.script
                      where l.text like '%南宫深%' group by l.script order by n desc limit 8"""):
    print("   ", r)

print()
print("== 留学：设置 M20008 的位置 ==")
for fn in sorted(os.listdir(r"D:\LegendOfMortal Wiki\data\raw\scripts")):
    if not fn.endswith(".txt"):
        continue
    s = open(os.path.join(r"D:\LegendOfMortal Wiki\data\raw\scripts", fn), encoding="utf-8").read()
    for m in re.finditer(r'SetFlag\(\s*"(M20008)"\s*,\s*([-\d.]+)', s):
        print("   ", fn, "→", m.group(2))

print()
print("== 含 梁有诗 与 叶云裳 的场景 ==")
for r in c.execute("""select s.script,s.title,s.chapter,
                        sum(case when l.text like '%梁有诗%' then 1 else 0 end) a,
                        sum(case when l.text like '%叶云裳%' then 1 else 0 end) b
                      from lines l join scenes s on s.script=l.script
                      group by l.script having a>0 and b>0 order by a+b desc limit 8"""):
    print("   ", r)
