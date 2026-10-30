# -*- coding: utf-8 -*-
import sqlite3, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

zero = []; one = []; more = []
for slug, secs in c.execute("select slug,sections from pages where type='地点'"):
    ss = json.loads(secs or "[]")
    rows = 0
    for s in ss:
        if s["h"] in ("考据来源", "脚注"):
            rows += len(s.get("rows") or [])
    (zero if rows == 0 else one if rows == 1 else more).append(slug)
print("地点页", len(zero) + len(one) + len(more), "｜无引用", len(zero), "｜1 条", len(one), "｜2+ 条", len(more))
print("无引用示例:", zero[:15])
print("只有1条示例:", one[:15])

print("\n===== intros_world 地点条目样例 =====")
d = json.load(open(r"D:\LegendOfMortal Wiki\data\intros_world.json", encoding="utf-8"))
for k in list(d)[:3]:
    print(k, list(d[k].keys()) if isinstance(d[k], dict) else type(d[k]))
