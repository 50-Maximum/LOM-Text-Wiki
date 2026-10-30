# -*- coding: utf-8 -*-
"""分析 294 场无地点：句数、章节、背景、前后场能否接力。"""
import io, json, os, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row
bg = json.load(open(os.path.join(BASE, "data", "scene_bg.json"), encoding="utf-8"))
no = []
for r in c.execute("select slug,sections from pages where type='场景'"):
    t = ""
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息":
            t = s.get("html") or ""
            break
    if "地点：" in t:
        continue
    no.append(r["slug"][len("场景/"):] if r["slug"].startswith("场景/") else r["slug"])

print("无地点", len(no))
info = {}
for sc in no:
    r = c.execute("select chapter,line_count from scenes where script=?", (sc,)).fetchone()
    info[sc] = (r["chapter"] if r else "?", r["line_count"] if r else -1)

lc = collections.Counter()
for sc in no:
    n = info[sc][1]
    lc["0句" if n <= 0 else ("1-5句" if n <= 5 else ("6-20句" if n <= 20 else "20句+"))] += 1
print("句数分布:", dict(lc))
print("章节分布:", collections.Counter(info[sc][0] for sc in no).most_common(8))
print("有背景:", sum(1 for sc in no if bg.get(sc)), "/", len(no))

# 边关系
edges = list(c.execute("select src,dst,type from scene_edges"))
prev = collections.defaultdict(list)
nxt = collections.defaultdict(list)
for s, d, t in edges:
    nxt[s].append((d, t))
    prev[d].append((s, t))
has_prev = sum(1 for sc in no if prev.get(sc))
has_next = sum(1 for sc in no if nxt.get(sc))
print("有入边:", has_prev, "有出边:", has_next)

print("\n样例 15:")
for sc in no[:15]:
    ch, n = info[sc]
    print("   %-30s %-6s %3d句 bg=%-14s prev=%s" % (
        sc, ch, n, ",".join((bg.get(sc) or [])[:1]) or "-",
        (prev.get(sc) or [("-", "")])[0][0]))
