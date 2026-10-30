# -*- coding: utf-8 -*-
import io, sys, os, re, glob, gzip, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
lib = json.loads(gzip.open(r"D:\LegendOfMortal Wiki\data\mod_res\LOMAssistant.conditions.json.gz", "rb").read().decode("utf-8"))
SW = lib["Switches"]
print("Travel 类键:")
for k in SW:
    if k.startswith("Travel"):
        print("   ", k, "->", SW[k])
tf = [p for p in glob.glob(r"D:\LegendOfMortal Wiki\data\raw\scripts\*.txt") if "travel" in os.path.basename(p).lower()]
print("\ntravel 脚本数:", len(tf))
cnt = collections.Counter()
for p in tf:
    t = open(p, encoding="utf-8", errors="replace").read()
    for cid in re.findall(r'checkpointmanager\.(?:Switch|Condition)\("([^"]+)"\)', t):
        cnt[cid] += 1
print("travel 脚本里的判定编号（前 15）:")
for k, v in cnt.most_common(15):
    print("   ", k, v, "->", SW.get(k))
print("其中有库文本的比例: %d/%d" % (sum(1 for k in cnt if k in SW), len(cnt)))
