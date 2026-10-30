# -*- coding: utf-8 -*-
"""统计地图事件原生标题（dev）覆盖情况，并列出缺名清单。"""
import io, json, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
d = json.load(open(r"D:\LegendOfMortal Wiki\data\position_events.json", encoding="utf-8"))
items = list(d.values()) if isinstance(d, dict) else d
has = [x for x in items if (x.get("dev") or "").strip()]
no = [x for x in items if not (x.get("dev") or "").strip()]
print("总数 %d  有原生名 %d  无原生名 %d" % (len(items), len(has), len(no)))

print("\n有原生名的样例:")
for x in has[:10]:
    print("   %-24s %s" % (x["name"], x["dev"]))

pref = collections.Counter((x["name"] or "").split("_")[0] for x in no)
print("\n缺名前缀分布:", pref.most_common(30))

# 重复 dev 名
dup = collections.Counter(x["dev"] for x in has)
print("\n重复原生名:", [(k, v) for k, v in dup.items() if v > 1][:10])
