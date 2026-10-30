# -*- coding: utf-8 -*-
"""查 conditions.json 里时间条件的实际写法与命中率。"""
import json, sys, io, re, os, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"E:\Game\steamapps\common\LegendOfMortal\BepInEx\plugins\LOMAssistant\StoryReview\conditions.json"
d = json.load(open(p, encoding="utf-8"))
sw, cd = d["Switches"], d["Conditions"]

pat = re.compile("目前时间|时间\\s*需|第[一二三四五六七八九十]+年")
hits_sw = {k: v for k, v in sw.items() if any(pat.search(str(x)) for x in v)}
hits_cd = {k: v for k, v in cd.items() if pat.search(str(v))}
print("Switches 含时间条件", len(hits_sw), "/", len(sw))
print("Conditions 含时间条件", len(hits_cd), "/", len(cd))
print()
for k, v in list(hits_sw.items())[:8]:
    print("S", k, v)
for k, v in list(hits_cd.items())[:8]:
    print("C", k, v)
print()
# 这些 id 在脚本里被引用多少次
scdir = r"D:\LegendOfMortal Wiki\data\raw\scripts"
ids = set(hits_sw) | set(hits_cd)
ref = collections.Counter()
for fn in os.listdir(scdir):
    if not fn.endswith(".txt"):
        continue
    s = open(os.path.join(scdir, fn), encoding="utf-8").read()
    for m in re.finditer(r'checkpointmanager\.(Switch|Condition)\(\s*"([^"]+)"', s):
        if m.group(2) in ids:
            ref[m.group(2)] += 1
print("被脚本引用的时间条件 id", len(ref), "总引用", sum(ref.values()))
for k, n in ref.most_common(10):
    print("   ", k, n, (sw.get(k) or cd.get(k)))
