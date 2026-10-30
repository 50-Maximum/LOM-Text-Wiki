# -*- coding: utf-8 -*-
import io, sys, os, re, glob, gzip, json, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
lib = json.loads(gzip.open(r"D:\LegendOfMortal Wiki\data\mod_res\LOMAssistant.conditions.json.gz", "rb").read().decode("utf-8"))
SW = lib["Switches"]
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
# 骰子行：按 (script, seq) 分组
rows = collections.defaultdict(list)
for sc, seq, idx, text, cond in c.execute("select script,seq,idx,text,cond from branch_nodes where kind='dice'"):
    rows[(sc, seq)].append((idx, text, cond))
print("骰子组数:", len(rows))
match = miss = 0
samples = []
for (sc, seq), lines in rows.items():
    cands = [f"{sc}_{seq+1:03d}", f"{sc}_{seq:03d}"]
    hit = next((k for k in cands if k in SW), None)
    if not hit:
        miss += 1
        continue
    v = SW[hit]
    match += 1
    if len(samples) < 6:
        samples.append((sc, seq, hit, v, [x[1][:18] for x in sorted(lines)][:5]))
print("能按 <脚本>_<序号> 对上库:", match, " 对不上:", miss)
for s in samples:
    print("\n  ", s[0], "seq", s[1], "id", s[2])
    print("     库:", s[3])
    print("     行:", s[4])
