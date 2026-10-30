# -*- coding: utf-8 -*-
"""为 25 个未映射地图事件找候选剧本：按事件名关键词在 scenes 里搜。"""
import io, sys, json, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
allsc = [r[0] for r in c.execute("select script from scenes")]
titles = dict(c.execute("select script,title from scenes"))

def find(pat, limit=12):
    rx = re.compile(pat, re.I)
    return [s for s in allsc if rx.search(s)][:limit]

for pat, label in [(r"section_01_07", "第一年七月段"),
                   (r"^travel", "旅行"),
                   (r"door", "门")]:
    got = find(pat, 20)
    print("\n=== %s ｜ %d 个（示例）" % (label, len(got)))
    for s in got:
        print("   %-40s %s" % (s, (titles.get(s) or "")[:26]))

print("\n=== Travel 类事件的 key 取值分布")
ev = json.load(open(B + r"\position_events.json", encoding="utf-8"))
for e in ev:
    if e["name"].startswith("Travel_"):
        print("   %-14s %-3s %-10s value=%-5s cond=%s"
              % (e["name"], e["key"], e.get("logic") or "", e.get("value"), e.get("cond")))
