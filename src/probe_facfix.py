# -*- coding: utf-8 -*-
import io, json, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki\data"
d = json.load(open(BASE + r"\factions_fix.json", encoding="utf-8"))
print("type:", type(d).__name__, "len:", len(d))
if isinstance(d, dict):
    ks = list(d)[:6]
    for k in ks:
        print("  ", k, "→", json.dumps(d[k], ensure_ascii=False)[:160])
elif isinstance(d, list):
    for x in d[:4]:
        print("  ", json.dumps(x, ensure_ascii=False)[:200])
print("\n有华山派?", "华山派" in d if isinstance(d, dict) else any("华山" in json.dumps(x, ensure_ascii=False) for x in d))
print("\n=== chars_prefix 抽样 ===")
cp = json.load(open(BASE + r"\chars_prefix.json", encoding="utf-8"))
cnt = collections.Counter(cp.values())
print("前缀种类", len(cnt))
print(sorted(cnt.items(), key=lambda x: -x[1])[:60])
