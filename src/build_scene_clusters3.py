# -*- coding: utf-8 -*-
"""分支簇 v3：限制在同章、限制深度与场数，避免一条支线吞掉整章。"""
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

MAX_SCENES = 40
MAX_DEPTH = 16


def chap(n):
    return NODES.get(n, {}).get("chapter") or ""


def walk(start, home_chap, shared):
    """从入口走，遇共享点/换章/超深即停。"""
    out, stack, dist = [], [(start, 0)], {start: 0}
    while stack and len(out) < MAX_SCENES:
        u, d = stack.pop(0)
        if d > MAX_DEPTH:
            continue
        if u != start and (u in shared or chap(u) != home_chap):
            continue
        if u not in out:
            out.append(u)
        for v in adj.get(u, []):
            if v not in dist:
                dist[v] = d + 1
                stack.append((v, d + 1))
    return out


clusters = []
cid = 0
for bp in BPS:
    src = bp["from"]
    alts = [a for a in bp["targets"] if a["to"] in NODES and a["to"] != src]
    if len(alts) < 2:
        continue
    home = chap(src)
    # 各路可达集合（同章、限深）
    reach = {}
    for i, a in enumerate(alts):
        seen, stack = {}, [(a["to"], 0)]
        while stack and len(seen) < 400:
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
        scs = walk(a["to"], home, shared)
        if scs:
            out.append({"results": a["results"], "entry": a["to"],
                        "type": a["type"], "scenes": scs})
    if len(out) < 2:
        continue
    if sum(len(a["scenes"]) for a in out) < 2:
        continue
    cid += 1
    clusters.append({"id": "C%04d" % cid, "src": src, "site": bp["site"],
                     "switch": bp["switch"],
                     "join": min(shared, key=lambda n: min(s.get(n, 99) for s in reach.values()))
                     if shared else "", "alts": out})

json.dump(clusters, open(os.path.join(BASE, "data", "scene_clusters.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)

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
print("按路线数:", dict(sorted(collections.Counter(min(6, len(c["alts"])) for c in clusters).items())))
for c in sorted(clusters, key=lambda x: -sum(len(a["scenes"]) for a in x["alts"]))[:4]:
    print("\n%s 判定=%s 源=%s%s" % (c["id"], c["switch"], c["src"],
                                 ("  汇合 " + c["join"]) if c["join"] else "  （无汇合）"))
    for a in c["alts"]:
        print("   结果%s：%d 场 入口 %s %s" % ("/".join(a["results"]), len(a["scenes"]),
                                          a["entry"], NODES.get(a["entry"], {}).get("title", "")))
