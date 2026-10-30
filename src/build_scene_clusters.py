# -*- coding: utf-8 -*-
"""第 2 步：分支簇。把「同一判定点的各条去路」各自能走到的场景归成一组互斥路线。

做法：
  1. 用主线/分支/转段边构图（不含战斗、回地图、结局）
  2. 每个判定点有 N 条去路（entry）
  3. 从每条去路往下走，取「各去路都能到达的最早节点」作为汇合点
  4. 汇合点之前、只属于某一路的场景，归到该路
输出 data/scene_clusters.json，供简介与页面用。
"""
import io, json, os, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
G = json.load(open(os.path.join(BASE, "data", "scene_graph.json"), encoding="utf-8"))
NODES = G["nodes"]
EDGES = G["edges"]
BPS = G["branch_points"]

FLOW = {"main", "branch", "story", "travel", "temp"}
adj = collections.defaultdict(list)
for e in EDGES:
    if e["type"] in FLOW and e["to"] in NODES:
        if e["to"] not in adj[e["from"]]:
            adj[e["from"]].append(e["to"])


def bfs(start, limit=600, depth=40):
    dist = {start: 0}
    q = collections.deque([start])
    while q and len(dist) < limit:
        u = q.popleft()
        if dist[u] >= depth:
            continue
        for v in adj.get(u, []):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


clusters = []
cid = 0
for bp in BPS:
    alts = [a for a in bp["targets"] if a["to"] in NODES]
    if len(alts) < 2:
        continue
    dists = {a["to"]: bfs(a["to"]) for a in alts}
    common = None
    for d in dists.values():
        s = set(d)
        common = s if common is None else (common & s)
    if not common:
        continue
    join = min(common, key=lambda n: (sum(d.get(n, 99) for d in dists.values()), -min(
        d.get(n, 99) for d in dists.values())))
    join_d = min(d.get(join, 99) for d in dists.values())
    if join_d <= 1:
        continue
    out_alts = []
    seen_any = collections.Counter()
    for a in alts:
        d = dists[a["to"]]
        scs = [n for n, k in d.items()
               if k > 0 and k < (d.get(join, 99) if join in d else 99)]
        out_alts.append({"results": a["results"], "entry": a["to"],
                         "type": a["type"], "scenes": sorted(scs, key=lambda n: d[n])})
        for n in scs:
            seen_any[n] += 1
    # 只保留独占场景（多路共用的是汇合前的公共段，不算择一）
    for a in out_alts:
        a["scenes"] = [n for n in a["scenes"] if seen_any[n] == 1]
    if sum(len(a["scenes"]) for a in out_alts) < 2:
        continue
    cid += 1
    clusters.append({"id": "C%04d" % cid, "src": bp["from"], "site": bp["site"],
                     "switch": bp["switch"], "join": join,
                     "alts": out_alts})

json.dump(clusters, open(os.path.join(BASE, "data", "scene_clusters.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)

# 场景 → 所属簇（取最小簇，避免嵌套外簇覆盖内簇）
scene_cluster = {}
for c in clusters:
    for i, a in enumerate(c["alts"], 1):
        for sc in a["scenes"]:
            cur = scene_cluster.get(sc)
            if cur is None or len(a["scenes"]) < cur["n"]:
                scene_cluster[sc] = {"cluster": c["id"], "alt": i, "n": len(a["scenes"]),
                                     "results": a["results"]}
json.dump(scene_cluster, open(os.path.join(BASE, "data", "scene_cluster_map.json"), "w",
                              encoding="utf-8"), ensure_ascii=False, indent=0)

print("分支簇 %d 个，覆盖场景 %d 个" % (len(clusters), len(scene_cluster)))
depth = collections.Counter(len(c["alts"]) for c in clusters)
print("按路线数:", dict(sorted(depth.items())))
big = sorted(clusters, key=lambda c: -sum(len(a["scenes"]) for a in c["alts"]))[:3]
for c in big:
    print("\n%s 判定=%s 源=%s 汇合=%s（%s）" % (
        c["id"], c["switch"], c["src"], c["join"], NODES.get(c["join"], {}).get("title", "")))
    for a in c["alts"]:
        print("   结果%s：%d 场，入口 %s" % ("/".join(a["results"]), len(a["scenes"]), a["entry"]))
