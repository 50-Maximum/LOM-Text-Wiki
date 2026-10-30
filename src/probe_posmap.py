# -*- coding: utf-8 -*-
"""地图事件 433 条里，哪些还没映射到剧本，长什么样。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
ev = json.load(open(B + r"\position_events.json", encoding="utf-8"))
mp = json.load(open(B + r"\position_script_map.json", encoding="utf-8"))
print("地图事件 %d 条，映射表 %d 条" % (len(ev), len(mp)))
print("映射表样例:", json.dumps(list(mp.items())[:3], ensure_ascii=False)[:300])

names = [e["name"] for e in ev]
uniq = sorted(set(names))
miss = [n for n in uniq if n not in mp]
print("\n去重事件名 %d，未映射 %d" % (len(uniq), len(miss)))
for n in miss:
    rows = [e for e in ev if e["name"] == n]
    print("  %-34s 条目%-3d key样例 %s" % (n, len(rows), (rows[0].get("key") or "")[:16]))
