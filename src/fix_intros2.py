# -*- coding: utf-8 -*-
"""修导语（稳健版）：百万赵活写进 slug 键；裴红腊门派改青城。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\intros_char.json"
d = json.load(open(p, encoding="utf-8"))

for k in [k for k in d if "百万" in k]:
    v = d[k]
    print("  键 %-16s 类型 %s 值 %s" % (k, type(v).__name__, str(v)[:70]))
    if isinstance(v, str):
        d[k] = ("百万赵活是梦境里的小竹所造的机关人。触发鹦鹉事件之后，梦中的鹦鹉会驾驶这具机关人出战，"
                "郁竹在梦里喊「出击，百万赵活」。")

for k in [k for k in d if "裴红腊" in k]:
    v = d[k]
    if isinstance(v, str):
        print("  裴红腊旧值:", v[:80])
        d[k] = v.replace("崆峒派", "青城派")
        print("  裴红腊新值:", d[k][:80])

json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("已写回")
