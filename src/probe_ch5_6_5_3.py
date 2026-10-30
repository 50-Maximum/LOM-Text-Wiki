# -*- coding: utf-8 -*-
"""挖 ch5_6_5_3「夺魄弟子急报惊变」的原始选项数据，看是否有选项条件。"""
import io, sys, os, json, sqlite3, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(B + r"\data\wiki.db").cursor()

S = "ch5_6_5_3"
print("=== choices 表")
for r in c.execute("select id,script,seq,checkpoint,options from choices where script=?", (S,)):
    print(" id=%s seq=%s checkpoint=%s" % (r[0], r[2], r[3]))
    print(" options:", r[4][:1500])

print("\n=== branch_nodes")
cols = [d[1] for d in c.execute("pragma table_info(branch_nodes)")]
print(" 列:", cols)
for r in c.execute("select * from branch_nodes where script=?", (S,)):
    print(" ", dict(zip(cols, r)))

print("\n=== flags")
for r in c.execute("select * from flags where script=?", (S,)):
    print(" ", r)

print("\n=== 原始剧本文件")
hits = []
for pat in ("data\\raw\\**\\*%s*" % S, "data\\raw\\*%s*" % S, "**\\*%s*.lua" % S):
    hits += glob.glob(os.path.join(B, pat), recursive=True)
hits = sorted(set(hits))
print(" 命中 %d 个" % len(hits))
for h in hits[:6]:
    print("  ", h, os.path.getsize(h), "字节")
