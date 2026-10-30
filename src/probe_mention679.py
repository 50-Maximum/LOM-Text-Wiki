# -*- coding: utf-8 -*-
"""分析 679 场「文中提及」档：有多少能靠 承前场 / 背景资源 补强。"""
import io, json, os, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row
bg = json.load(open(os.path.join(BASE, "data", "scene_bg.json"), encoding="utf-8"))
aud = json.load(open(os.path.join(BASE, "data", "place_audit.json"), encoding="utf-8"))

rows = []
for r in c.execute("select slug,sections from pages where type='场景'"):
    loc = ""
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息":
            loc = s.get("html") or ""
            break
    if "（依据：文中提及）" not in loc:
        continue
    import re
    m = re.search(r"地点：([^（。]+)（", loc)
    rows.append((r["slug"][3:], m.group(1) if m else ""))

print("文中提及档", len(rows))
withbg = sum(1 for sc, p in rows if bg.get(sc))
print("有背景记录", withbg, "无背景", len(rows) - withbg)

# 前置场景：用 scene_next 表或 scene_edges
try:
    nxt = {r[0]: r[1] for r in c.execute("select script,next_script from scene_next")}
    print("scene_next 条数", len(nxt))
except Exception as e:
    nxt = {}
    print("无 scene_next:", e)

# 地点的短名（去门派前缀）
def short(p):
    return p.split("-")[-1] if p else ""

print("\n地点分布 top15:")
for k, v in collections.Counter(p for _, p in rows).most_common(15):
    print("   %-22s %d" % (k, v))

print("\n背景分布 top10:")
cnt = collections.Counter()
for sc, p in rows:
    for b in (bg.get(sc) or [])[:1]:
        cnt[b] += 1
for k, v in cnt.most_common(10):
    print("   %-26s %d" % (k, v))
