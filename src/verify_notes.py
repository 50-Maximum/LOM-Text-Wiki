# -*- coding: utf-8 -*-
"""校验 notes 的引文是否真落在指定场景的句区间内。"""
import os, sys, io, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

rows = c.execute("select script,seq_from,seq_to,type,name,note,quote from notes").fetchall()
print("notes", len(rows))
cache = {}

def seg(script, a, b):
    if script not in cache:
        cache[script] = {r[0]: (r[1] or "") for r in
                         c.execute("select seq,text from lines where script=?", (script,))}
    d = cache[script]
    lo, hi = min(a, b), max(a, b)
    return "".join(d.get(i, "") for i in range(lo, hi + 1))

bad, ok = [], 0
for s, a, b, t, n, note, q in rows:
    if not q:
        bad.append((s, a, b, n, note, q, "空引文"))
        continue
    body = seg(s, a, b).replace("\n", "")
    qq = q.replace("\n", "").replace(" ", "")
    if qq and qq in body:
        ok += 1
    else:
        bad.append((s, a, b, n, note, q, "对不上"))

print(f"引文命中 {ok}｜不命中 {len(bad)}（{len(bad)/max(1,len(rows))*100:.1f}%）")
print("\n不命中样本:")
for x in bad[:12]:
    print("  ", x[0], x[1], x[2], x[3], "|", x[5][:40], "|", x[6])

print("\n== 招亲场景 ch5_3_1 的笔记 ==")
for r in c.execute("select seq_from,seq_to,type,name,note,quote from notes where script='ch5_3_1' order by seq_from"):
    print(f"  [{r[0]:3}-{r[1]:3}] {r[2]:8} {r[3]}｜{r[4]}")
    print(f"        引: {r[5]}")
