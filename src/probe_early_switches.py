# -*- coding: utf-8 -*-
import io, sys, os, re, glob, gzip, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
lib = json.loads(gzip.open(r"D:\LegendOfMortal Wiki\data\mod_res\LOMAssistant.conditions.json.gz", "rb").read().decode("utf-8"))
SW, CD = lib["Switches"], lib["Conditions"]
base = r"D:\LegendOfMortal Wiki\data\raw\scripts"
stat = collections.Counter()
samples = []
for f in sorted(glob.glob(os.path.join(base, "*.txt"))):
    ls = open(f, encoding="utf-8", errors="replace").read().splitlines()
    first_say = next((i for i, l in enumerate(ls) if l.strip().startswith("say(")), len(ls))
    ids = []
    for ln in ls[:first_say]:
        for m in re.finditer(r'checkpointmanager\.(?:Switch|Condition)\("([^"]+)"\)', ln):
            ids.append(m.group(1))
    if not ids:
        continue
    stat["有开场判定脚本"] += 1
    known = [i for i in ids if i in SW or i in CD]
    if known:
        stat["其中有库文本"] += 1
        if len(samples) < 8:
            samples.append((os.path.basename(f), first_say, [(k, SW.get(k) or CD.get(k)) for k in known[:3]]))
print(dict(stat))
for s in samples:
    print("  ", s[0], "首个say行", s[1], s[2])
