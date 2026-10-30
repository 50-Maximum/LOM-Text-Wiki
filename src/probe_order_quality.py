# -*- coding: utf-8 -*-
"""检查时间线质量：章节是否被旗标依赖打乱。"""
import sqlite3, sys, io, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

rows = c.execute("""select o.ord,o.script,o.chapter,s.title from scene_order o
                    left join scenes s on s.script=o.script order by o.ord""").fetchall()
print("总数", len(rows))
where = {r[1]: r[0] for r in rows}
print("act2_2 ->", where.get("act2_2"), " act2_1 ->", where.get("act2_1"), " act2_3 ->", where.get("act2_3"))

def rank(ch):
    ch = ch or ""
    if ch == "序章": return 0
    m = re.match(r"第(\d+)章", ch)
    if m: return 1 + int(m.group(1))
    if ch == "支线": return 100
    if ch == "角色线": return 200
    if ch == "其他": return 300
    return 400

seq = [(r[0], rank(r[2]), r[1], r[2], r[3]) for r in rows]
inv = 0
worst = []
for i in range(1, len(seq)):
    if seq[i][1] < seq[i-1][1]:
        inv += 1
        if len(worst) < 12:
            worst.append((seq[i-1], seq[i]))
print("章节逆序次数", inv)
for a, b in worst:
    print(f"   {a[0]:4} {a[2]:24} {a[3]}  →  {b[0]:4} {b[2]:24} {b[3]}")

print("\n各章起止序号:")
by = collections.defaultdict(list)
for r in seq:
    by[r[3]].append(r[0])
for ch, arr in by.items():
    print(f"  {ch:6} {min(arr):4} ~ {max(arr):4}  {len(arr)} 场")
