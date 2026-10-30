# -*- coding: utf-8 -*-
import io, sys, os, re, glob, gzip, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
lib = json.loads(gzip.open(r"D:\LegendOfMortal Wiki\data\mod_res\LOMAssistant.conditions.json.gz", "rb").read().decode("utf-8"))
SW, CD = lib["Switches"], lib["Conditions"]
base = r"D:\LegendOfMortal Wiki\data\raw\scripts"
fs = sorted(glob.glob(os.path.join(base, "*.txt")))
tot = collections.Counter()
hit = collections.Counter()
samples = []
for f in fs:
    t = open(f, encoding="utf-8", errors="replace").read()
    for kind, pat in (("Switch", r'checkpointmanager\.Switch\("([^"]+)"\)'),
                      ("Condition", r'checkpointmanager\.Condition\("([^"]+)"\)')):
        for m in re.finditer(pat, t):
            i = m.group(1)
            tot[kind] += 1
            if i in SW or i in CD:
                hit[kind] += 1
                if len(samples) < 6:
                    samples.append((os.path.basename(f), kind, i, SW.get(i) or CD.get(i)))
print("引用统计:", dict(tot))
print("库中命中:", dict(hit), " 命中率: %.1f%%" % (100.0 * sum(hit.values()) / max(1, sum(tot.values()))))
for s in samples:
    print("  ", s[0], s[1], s[2], "->", str(s[3])[:120])
# 库里 Switches 值形态
print("\nSwitches 值样例:")
for k in list(SW)[:3]:
    print("  ", k, "->", SW[k])
print("\nConditions 值样例:")
for k in list(CD)[:5]:
    print("  ", k, "->", str(CD[k])[:100])
