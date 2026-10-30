# -*- coding: utf-8 -*-
"""场景图：节点=场景，边=剧本里的跳转（带条件、结果序号、类型）。

边类型：
  main     无条件接续（SetNextScript 不在 if 里）
  branch   if/elseif 里的跳转（同一分支点择一）
  ending   ChangeScene 到 GameOver / 结局
  map      ChangeScene 到养成地图等非剧情目标
  travel   赶路剧本（SetCurrentTravelScript）
  story    跳去另一段剧本（SetCurrentStoryScript）
  temp     临时剧本

输出 data/scene_graph.json + 库表 scene_edges
"""
import io, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
SRC = os.path.join(BASE, "data", "raw", "scripts")
DB = os.path.join(BASE, "data", "wiki.db")

RE_CALL = re.compile(r'(SetNextScript|SetCurrentStoryScript|SetCurrentTravelScript|SetTempScript|ChangeScene)'
                     r'\s*\(\s*(?:\d+\s*,\s*)?"([^"]+)"')
RE_IF = re.compile(r'^\s*(if|elseif)\b(.*?)\bthen\b')
RE_ELSE = re.compile(r'^\s*else\s*$')
RE_END = re.compile(r'^\s*end\s*$')
RE_LOCAL = re.compile(r'^\s*local\s+(\w+)\s*=\s*checkpointmanager\.(\w+)\("([^"]+)"\)')
RE_SW = re.compile(r'(\w+)\s*==\s*(\d+)')
RE_TOK = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")

KIND = {"SetNextScript": "main", "SetCurrentStoryScript": "story",
        "SetCurrentTravelScript": "travel", "SetTempScript": "temp",
        "ChangeScene": "map"}

MAP_WORDS = ("GameOver", "End", "Map", "map", "Title", "Ending")


def parse(path, cond_lib):
    edges = []
    stack = []      # 条件栈
    ck = {}         # 变量 → (Switch/Condition, id)
    for no, ln in enumerate(open(path, encoding="utf-8-sig", errors="replace"), 1):
        m = RE_LOCAL.match(ln)
        if m:
            ck[m.group(1)] = (m.group(2), m.group(3))
            continue
        m = RE_IF.match(ln)
        if m:
            cond = (m.group(2) or "").strip()
            if m.group(1) == "elseif":
                if stack:
                    stack[-1] = cond
            else:
                stack.append(cond)
            continue
        if RE_ELSE.match(ln):
            if stack:
                stack[-1] = "否则"
            continue
        if RE_END.match(ln):
            if stack:
                stack.pop()
            continue
        m = RE_CALL.search(ln)
        if not m:
            continue
        fn, target = m.group(1), m.group(2)
        cond = " / ".join(x for x in stack if x)
        sw_id, sw_res = "", ""
        for _entry in reversed(stack):
            for var, res in RE_SW.findall(_entry or ""):
                if var in ck and ck[var][0] == "Switch":
                    sw_id, sw_res = ck[var][1], res
                    break
            if sw_id:
                break
        ids = [t for t in set(RE_TOK.findall(cond)) if t in cond_lib]
        etype = KIND.get(fn, "main")
        if fn == "SetNextScript":
            etype = "branch" if cond else "main"
        if fn == "ChangeScene" and target.startswith("GameOver"):
            etype = "ending"
        elif fn == "ChangeScene" and any(w in target for w in ("Map", "map", "Title")):
            etype = "map"
        elif fn == "ChangeScene":
            etype = "scene"
        edges.append({"from": "", "to": target, "type": etype, "fn": fn,
                      "cond": cond, "cond_ids": ids, "switch": sw_id, "result": sw_res,
                      "line": no})
    return edges


def main():
    cond_lib = {}
    p = os.path.join(BASE, "data", "cond_lib.json")
    if os.path.exists(p):
        cond_lib = json.load(open(p, encoding="utf-8"))

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    sc = {r["script"]: dict(r) for r in con.execute(
        "select script,title,chapter,line_count from scenes")}

    nodes = {}
    edges = []
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith(".txt"):
            continue
        s = fn[:-4]
        es = parse(os.path.join(SRC, fn), cond_lib)
        for e in es:
            e["from"] = s
        edges.extend(es)
        nodes[s] = {"title": sc.get(s, {}).get("title") or "",
                    "chapter": sc.get(s, {}).get("chapter") or "",
                    "lines": sc.get(s, {}).get("line_count") or 0,
                    "out": len(es)}

    # 分支点：同源 + 同判定 + 结果号
    bp = collections.defaultdict(list)
    for e in edges:
        if e["switch"] and e["result"]:
            bp[(e["from"], e["switch"])].append(e)
    branch_points = []
    for (src, sw), es in bp.items():
        tgt, _by = [], {}
        for e in sorted(es, key=lambda x: (int(x["result"] or 0), len(x["cond"] or ""))):
            d = _by.get(e["to"])
            if d is None:
                d = {"results": [], "to": e["to"], "type": e["type"]}
                _by[e["to"]] = d
                tgt.append(d)
            if e["result"] not in d["results"]:
                d["results"].append(e["result"])
        branch_points.append({"from": src, "switch": sw, "n": len(tgt), "targets": tgt})

    # 统计
    by_type = collections.Counter(e["type"] for e in edges)
    main_next = {}
    for e in edges:
        if e["type"] == "main":
            main_next[e["from"]] = e["to"]
    outs = collections.defaultdict(set)
    for e in edges:
        outs[e["from"]].add(e["to"])
    ins = collections.defaultdict(set)
    for e in edges:
        ins[e["to"]].add(e["from"])

    known = set(nodes)
    unknown_targets = collections.Counter(
        e["to"] for e in edges if e["to"] not in known)
    orphans = [s for s in nodes if not outs.get(s) and not any(
        e["type"] == "ending" and e["from"] == s for e in edges)]

    graph = {
        "built_for": "1.0.6001.0",
        "nodes": nodes,
        "edges": edges,
        "main_next": main_next,
        "branch_points": branch_points,
    }
    json.dump(graph, open(os.path.join(BASE, "data", "scene_graph.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=0, sort_keys=True)

    # 入库
    con.execute("drop table if exists scene_edges")
    con.execute("""create table scene_edges(
        src text, dst text, type text, fn text, cond text, switch text, result text, line int)""")
    con.executemany("insert into scene_edges values(?,?,?,?,?,?,?,?)",
                    [(e["from"], e["to"], e["type"], e["fn"], e["cond"],
                      e["switch"], e["result"], e["line"]) for e in edges])
    con.commit()

    print("节点 %d ／ 边 %d" % (len(nodes), len(edges)))
    print("边类型:", dict(by_type))
    print("分支点:", len(branch_points), "（含判定 id 的分支）")
    print("有去向的场景 %d ／ 无去向 %d" % (len(outs), len(orphans)))
    print("\n未解析到的目标 top8:", unknown_targets.most_common(8))
    print("\n分支点示例:")
    for b in branch_points[:3]:
        print("  %s = %s 共 %d 个结果" % (b["from"], b["switch"], b["n"]))
        for t in b["targets"]:
            print("     结果%s → %s（%s）%s" % ("/".join(t["results"]), t["to"], t["type"],
                                            nodes.get(t["to"], {}).get("title", "")))
    con.close()


main()
