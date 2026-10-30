# -*- coding: utf-8 -*-
"""分支簇 v4：取消 40 场硬截断、保留嵌套簇（外层与内层都记），供页面同时展示。

改动：
- MAX_SCENES 40 → 400，MAX_DEPTH 16 → 40；触顶时标 truncated（不静默丢）
- scene_cluster_map 每个场景记录全部所属簇（all），旧的单值字段保留给兼容
"""
import io, json, os, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
G = json.load(open(os.path.join(BASE, "data", "scene_graph.json"), encoding="utf-8"))
NODES, EDGES, BPS = G["nodes"], G["edges"], G["branch_points"]

FLOW = {"main", "branch", "story", "travel", "temp"}
adj = collections.defaultdict(list)
for e in EDGES:
    if e["type"] in FLOW and e["to"] in NODES and e["to"] not in adj[e["from"]]:
        adj[e["from"]].append(e["to"])

MAX_SCENES = 400
MAX_DEPTH = 40

def chap(n):
    return NODES.get(n, {}).get("chapter") or ""

def walk(start, home_chap, shared):
    out, stack, dist = [], [(start, 0)], {start: 0}
    truncated = False
    while stack:
        if len(out) >= MAX_SCENES:
            truncated = True
            break
        u, d = stack.pop(0)
        if d > MAX_DEPTH:
            truncated = True
            continue
        if u != start and (u in shared or chap(u) != home_chap):
            continue
        if u not in out:
            out.append(u)
        for v in adj.get(u, []):
            if v not in dist:
                dist[v] = d + 1
                stack.append((v, d + 1))
    return out, truncated

clusters, cid = [], 0
for bp in BPS:
    src = bp["from"]
    alts = [a for a in bp["targets"] if a["to"] in NODES and a["to"] != src]
    if len(alts) < 2:
        continue
    home = chap(src)
    reach = {}
    for i, a in enumerate(alts):
        seen, stack = {}, [(a["to"], 0)]
        while stack and len(seen) < 600:
            u, d = stack.pop(0)
            if d > MAX_DEPTH or u in seen:
                continue
            if u != a["to"] and chap(u) != home:
                continue
            seen[u] = d
            for v in adj.get(u, []):
                if v not in seen:
                    stack.append((v, d + 1))
        reach[i] = seen
    touch = collections.Counter()
    for s in reach.values():
        for n in s:
            touch[n] += 1
    shared = {n for n, k in touch.items() if k >= 2}
    out = []
    for i, a in enumerate(alts):
        scs, tr = walk(a["to"], home, shared)
        if scs:
            out.append({"results": a["results"], "entry": a["to"], "type": a["type"],
                        "scenes": scs, "truncated": tr})
    if len(out) < 2:
        continue
    if sum(len(a["scenes"]) for a in out) < 2:
        continue
    cid += 1
    clusters.append({"id": "C%04d" % cid, "src": src, "site": bp["site"], "switch": bp["switch"],
                     "join": min(shared, key=lambda n: min(s.get(n, 99) for s in reach.values()))
                     if shared else "", "alts": out,
                     "total": sum(len(a["scenes"]) for a in out)})

json.dump(clusters, open(os.path.join(BASE, "data", "scene_clusters.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)

bysize = {c["id"]: c["total"] for c in clusters}
scene_cluster = {}
for c in clusters:
    for i, a in enumerate(c["alts"], 1):
        for sc in a["scenes"]:
            rec = scene_cluster.setdefault(sc, {"all": []})
            rec["all"].append({"cluster": c["id"], "alt": i, "n": len(a["scenes"]),
                               "results": a["results"], "total": c["total"]})
            rec["all"].sort(key=lambda m: -m["total"])
            rec["cluster"] = rec["all"][0]["cluster"]
            rec["alt"] = rec["all"][0]["alt"]
            rec["n"] = rec["all"][0]["n"]
            rec["results"] = rec["all"][0]["results"]

json.dump(scene_cluster, open(os.path.join(BASE, "data", "scene_cluster_map.json"), "w",
                              encoding="utf-8"), ensure_ascii=False, indent=0)

multi = sum(1 for v in scene_cluster.values() if len(v["all"]) > 1)
trunc = sum(1 for c in clusters for a in c["alts"] if a.get("truncated"))
print("分支簇 %d 个，覆盖场景 %d 个（多簇场景 %d，触顶截断路 %d）"
      % (len(clusters), len(scene_cluster), multi, trunc))
for c in sorted(clusters, key=lambda x: -x["total"])[:4]:
    print("\n%s 判定=%s 源=%s 合计 %d 场" % (c["id"], c["switch"], c["src"], c["total"]))
    for a in c["alts"]:
        print("   结果%s：%d 场%s" % ("/".join(a["results"]), len(a["scenes"]),
                                   "（截断）" if a.get("truncated") else ""))
