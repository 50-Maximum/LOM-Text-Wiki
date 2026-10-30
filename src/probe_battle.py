# -*- coding: utf-8 -*-
"""摸清战斗节点写法：Combat / Battle / 结果分支，为「战斗结果→剧情分叉」打底。"""
import io, os, re, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAW = r"D:\LegendOfMortal Wiki\data\raw\scripts"
pats = {
    "Combat(": re.compile(r'Combat\("([^"]+)"'),
    "Battle(": re.compile(r'Battle\("([^"]+)"'),
    "Battle_Result": re.compile(r'Battle_Result'),
    "Combat_Result": re.compile(r'Combat_Result'),
    "ChangeScene": re.compile(r'ChangeScene\("([^"]+)"'),
}
cnt = collections.Counter()
samples = collections.defaultdict(list)
ids = collections.defaultdict(set)
for fn in os.listdir(RAW):
    if not fn.endswith(".txt"):
        continue
    sc = fn[:-4]
    t = open(os.path.join(RAW, fn), encoding="utf-8", errors="ignore").read()
    for k, rx in pats.items():
        ms = rx.findall(t)
        if ms:
            cnt[k] += 1
            for m in ms[:3]:
                if isinstance(m, str):
                    ids[k].add(m)
            if len(samples[k]) < 3:
                samples[k].append(sc)

print("含该写法的剧本数:", dict(cnt))
for k in samples:
    print("\n==", k, "样例脚本:", samples[k])
    print("   取值样例:", list(ids[k])[:6])

# 结果分支写法
res_pats = {
    "if result ==": re.compile(r'if\s+\w*result\w*\s*=='),
    "if win": re.compile(r'if\s+win'),
    "if lose": re.compile(r'if\s+lose'),
    "battlewin": re.compile(r'battlew|BattleWin|battlewin'),
}
c2 = collections.Counter()
for fn in os.listdir(RAW):
    if not fn.endswith(".txt"):
        continue
    t = open(os.path.join(RAW, fn), encoding="utf-8", errors="ignore").read()
    for k, rx in res_pats.items():
        if rx.search(t):
            c2[k] += 1
print("\n结果判断写法:", dict(c2))
