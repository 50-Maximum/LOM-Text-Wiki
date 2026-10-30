# -*- coding: utf-8 -*-
import io, json, os, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\extra_persons.json"
print("exists", os.path.exists(p))
d = json.load(open(p, encoding="utf-8"))
print("count", len(d))
cnt = collections.Counter((v or {}).get("faction") or "江湖" for v in d.values())
for k, n in cnt.most_common():
    print("   %-10s %d" % (k, n))
print("\n岭南派/崆峒 的人：")
for k, v in d.items():
    f = (v or {}).get("faction") or ""
    if f in ("岭南派", "崆峒", "巫灵教", "嵩山寺", "孤云山派", "华山派"):
        print("   ", k, "→", f, (v or {}).get("sub") or "")
