# -*- coding: utf-8 -*-
"""统计地图事件的 key 文案与代码前缀，设计命名规则。"""
import io, json, re, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from opencc import OpenCC  # 若不可用则退回手工
try:
    cc = OpenCC("t2s")
except Exception:
    cc = None

d = json.load(open(r"D:\LegendOfMortal Wiki\data\position_events.json", encoding="utf-8"))
items = list(d.values()) if isinstance(d, dict) else d
print("条数", len(items))

def s2s(x):
    try:
        return cc.convert(x) if cc else x
    except Exception:
        return x

keys = collections.Counter(it.get("key") or "" for it in items)
print("\nkey 样例 20:")
for k, n in keys.most_common(20):
    print("   %-16s ×%d  → %s" % (k, n, s2s(k)))

pref = collections.Counter((it.get("name") or "").split("_")[0] for it in items)
print("\n代码前缀:", pref.most_common(12))
