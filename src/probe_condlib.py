# -*- coding: utf-8 -*-
import io, sys, gzip, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\mod_res\LOMAssistant.conditions.json.gz"
j = json.loads(gzip.open(p, "rb").read().decode("utf-8"))
print("Version:", j.get("Version"))
for k, v in j.items():
    if k == "Version":
        continue
    print("\n== %s == type=%s len=%s" % (k, type(v).__name__, len(v) if hasattr(v, "__len__") else "?"))
    if isinstance(v, dict):
        ks = list(v)[:5]
        for kk in ks:
            print("   key:", kk, "->", str(v[kk])[:300])
    elif isinstance(v, list):
        for x in v[:3]:
            print("   item:", str(x)[:300])
