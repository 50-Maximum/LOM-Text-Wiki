# -*- coding: utf-8 -*-
"""评估：无名地图事件对应的场景标题，哪些是描述性标题，哪些只是编号翻版。"""
import io, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
items = json.load(open(os.path.join(BASE, "data", "position_events.json"), encoding="utf-8"))
pm = json.load(open(os.path.join(BASE, "data", "position_script_map.json"), encoding="utf-8"))
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row

BAD = re.compile(r"（\d+）$|・工作$|^转场")
good, bad, miss = [], [], []
for x in items:
    if (x.get("dev") or "").strip():
        continue
    sc = pm.get(x["name"])
    r = c.execute("select title,line_count from scenes where script=?", (sc,)).fetchone() if sc else None
    if not r:
        miss.append(x["name"]); continue
    t = r["title"] or ""
    (good if not BAD.search(t) else bad).append((x["name"], t, r["line_count"]))

print("描述性标题 %d ／ 编号式标题 %d ／ 无剧本 %d" % (len(good), len(bad), len(miss)))
print("\n描述性样例:")
for a, b, n in good[:12]:
    print("   %-24s %s（%d句）" % (a, b, n))
print("\n编号式样例:")
for a, b, n in bad[:8]:
    print("   %-24s %s（%d句）" % (a, b, n))
print("\n长度分布(描述性):", collections.Counter(len(b) for a, b, n in good).most_common(6))
