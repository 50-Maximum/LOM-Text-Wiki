# -*- coding: utf-8 -*-
"""按前缀抽样，看哪些事件已有中文名（dev），用于定别名规则。"""
import io, json, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
d = json.load(open(r"D:\LegendOfMortal Wiki\data\position_events.json", encoding="utf-8"))
items = list(d.values()) if isinstance(d, dict) else d

by_pref = collections.defaultdict(list)
for it in items:
    nm = it.get("name") or ""
    by_pref[nm.split("_")[0]].append(it)

for pref, lst in sorted(by_pref.items(), key=lambda x: -len(x[1])):
    named = [x for x in lst if (x.get("dev") or "").strip()]
    print("\n%-10s 共%3d 有中文名%3d" % (pref, len(lst), len(named)))
    for x in named[:2]:
        print("    %-22s → %s" % (x.get("name"), x.get("dev")))
    for x in lst[:1]:
        print("    样例键: %s | key=%s" % (x.get("name"), x.get("key")))
