# -*- coding: utf-8 -*-
"""看清两个问题：①招亲场景证据错配 ②路线选择在脚本里怎么编码。"""
import sqlite3, sys, io, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== 第5章·2 的场景 ==")
for r in c.execute("select script,title,line_count,place from scenes where chapter like '第5章·2%' order by line_count desc"):
    print("  ", r)

print()
print("== 「我要杀了你」出现在哪 ==")
for r in c.execute("select script,seq,speaker,substr(text,1,40) from lines where text like '%我要杀了你%'"):
    print("  ", r)

print()
print("== 招亲场景里赵活与南宫深的对话（前后 12 句）==")
row = c.execute("select script from scenes where chapter='第5章·2' order by line_count desc limit 1").fetchone()
sc = row[0]
lines = c.execute("select seq,speaker,text from lines where script=? order by seq", (sc,)).fetchall()
print("  脚本", sc, "共", len(lines), "句")
hit = [i for i, (q, sp, tx) in enumerate(lines) if "南宫深" in (tx or "") and sp == "赵活"]
print("  赵活提南宫深的位置", hit[:5])
for i in hit[:1]:
    for j in range(max(0, i - 4), min(len(lines), i + 6)):
        q, sp, tx = lines[j]
        print(f"   #{q} {sp}: {(tx or '').replace(chr(10),' ')[:70]}")

print()
print("== 脚本里的选择点（含 青城/崆峒/留学）==")
d = r"D:\LegendOfMortal Wiki\data\raw\scripts"
cnt = 0
for fn in sorted(os.listdir(d)):
    if not fn.endswith(".txt"):
        continue
    s = open(os.path.join(d, fn), encoding="utf-8").read()
    if "留学" in s or ("青城" in s and "崆峒" in s):
        print("  ", fn, "｜青城", s.count("青城"), "崆峒", s.count("崆峒"), "留学", s.count("留学"))
        cnt += 1
        if cnt > 12:
            break
