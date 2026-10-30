# -*- coding: utf-8 -*-
"""第 2 步 v2：分支簇（不强求汇合点，按「只属于这一路的场景」归组）。

规则：
  1. 每个判定点有 N 条去路
  2. 每路从入口向下走（只走剧情边），遇到「别的路也能走到的节点」即停（那是汇合或互串）
  3. 停下来的部分里，独占场景归这一路
  4. 没有汇合的永久分叉也照样成簇（结局/地图前各自走完）
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


def bfs(start, limit=900, depth=60):
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
scene_cluster = {}
cid = 0
for bp in BPS:
    alts = [a for a in bp["targets"] if a["to"] in NODES]
    if len(alts) < 2:
        continue
    dists = {i: bfs(a["to"]) for i, a in enumerate(alts)}
    touch = collections.Counter()
    for d in dists.values():
        for n in d:
            touch[n] += 1
    shared = {n for n, k in touch.items() if k >= 2}
    out = []
    for i, a in enumerate(alts):
        d = dists[i]
        mine = [n for n in d if touch[n] == 1 and n not in shared]
        # 从入口出发，遇到共享节点就停（保证不是绕远绕回来的）
        keep, stack, seen = [], [a["to"]], set()
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            if u in shared and u != a["to"]:
                continue
            keep.append(u)
            for v in adj.get(u, []):
                if v not in seen:
                    stack.append(v)
        if not keep:
            keep = [a["to"]]
        out.append({"results": a["results"], "entry": a["to"], "type": a["type"],
                    "scenes": sorted(set(keep), key=lambda n: dists[i].get(n, 99))})
    if sum(len(a["scenes"]) for a in out) < 2:
        continue
    if len({tuple(a["scenes"]) for a in out}) < 2:
        continue
    shared_join = ""
    if shared:
        shared_join = min(shared, key=lambda n: min(d.get(n, 99) for d in dists.values()))
    cid += 1
    clusters.append({"id": "C%04d" % cid, "src": bp["from"], "site": bp["site"],
                     "switch": bp["switch"], "join": shared_join, "alts": out})

json.dump(clusters, open(os.path.join(BASE, "data", "scene_clusters.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)

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
sizes = collections.Counter()
for c in clusters:
    sizes[min(6, len(c["alts"]))] += 1
print("按路线数:", dict(sorted(sizes.items())))
tot = sum(len(a["scenes"]) for c in clusters for a in c["alts"])
print("归属场景总次数 %d（含嵌套）" % tot)
for c in sorted(clusters, key=lambda x: -sum(len(a["scenes"]) for a in x["alts"]))[:4]:
    print("\n%s 判定=%s 源=%s%s" % (c["id"], c["switch"], c["src"],
                                 ("  汇合 " + c["join"]) if c["join"] else "  （无汇合，永久分叉）"))
    for a in c["alts"]:
        t = NODES.get(a["entry"], {}).get("title", "")
        print("   结果%s：%d 场  入口 %s %s" % ("/".join(a["results"]), len(a["scenes"]), a["entry"], t))
