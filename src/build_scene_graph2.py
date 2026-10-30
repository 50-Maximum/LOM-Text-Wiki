# -*- coding: utf-8 -*-
"""场景图 v2：按 if 语句位置归组分支点，避免同一判定的多处判定被并成一堆。

边类型：main / branch / ending / map / scene / story / travel / temp
分支点：同一场景、同一 if 位置、同一判定 → 一组，结果号互斥。
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


def parse(path, cond_lib):
    edges = []
    stack = []       # [{"cond":str,"line":int,"sw":str,"res":str}]
    ck = {}
    for no, ln in enumerate(open(path, encoding="utf-8-sig", errors="replace"), 1):
        m = RE_LOCAL.match(ln)
        if m:
            ck[m.group(1)] = (m.group(2), m.group(3))
            continue
        m = RE_IF.match(ln)
        if m:
            cond = (m.group(2) or "").strip()
            sw, res = "", ""
            for var, r in RE_SW.findall(cond):
                if var in ck and ck[var][0] == "Switch":
                    sw, res = ck[var][1], r
                    break
            if m.group(1) == "elseif" and stack:
                stack[-1] = {"cond": cond, "line": stack[-1]["line"], "sw": sw, "res": res}
            else:
                stack.append({"cond": cond, "line": no, "sw": sw, "res": res})
            continue
        if RE_ELSE.match(ln):
            if stack:
                stack[-1] = {"cond": "否则", "line": stack[-1]["line"], "sw": "", "res": ""}
            continue
        if RE_END.match(ln):
            if stack:
                stack.pop()
            continue
        m = RE_CALL.search(ln)
        if not m:
            continue
        fn, target = m.group(1), m.group(2)
        cond = " / ".join(x["cond"] for x in stack if x["cond"])
        site = ""
        sw, res = "", ""
        for fr in reversed(stack):
            if fr["sw"]:
                site, sw, res = fr["line"], fr["sw"], fr["res"]
                break
        if fn == "SetNextScript":
            etype = "branch" if cond else "main"
        elif fn == "ChangeScene":
            if target.startswith("GameOver"):
                etype = "ending"
            elif any(w in target for w in ("Map", "Title")):
                etype = "map"
            else:
                etype = "scene"
        else:
            etype = {"SetCurrentStoryScript": "story", "SetCurrentTravelScript": "travel",
                     "SetTempScript": "temp"}.get(fn, "main")
        edges.append({"from": "", "to": target, "type": etype, "fn": fn, "cond": cond,
                      "cond_ids": [t for t in set(RE_TOK.findall(cond)) if t in cond_lib],
                      "switch": sw, "result": res, "site": site, "line": no})
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

    nodes, edges = {}, []
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

    bp = collections.defaultdict(list)
    _used = set()
    for e in sorted(edges, key=lambda x: x["line"]):
        if not (e["switch"] and e["result"]):
            continue
        if e["to"] == e["from"]:
            continue
        _k = (e["from"], e["switch"], e["site"], e["result"])
        if _k in _used:
            continue
        _used.add(_k)
        bp[(e["from"], e["switch"], e["site"])].append(e)
    branch_points = []
    for (src, sw, site), es in bp.items():
        tgt, _by = [], {}
        for e in es:
            d = _by.get(e["to"])
            if d is None:
                d = {"results": [], "to": e["to"], "type": e["type"]}
                _by[e["to"]] = d
                tgt.append(d)
            if e["result"] not in d["results"]:
                d["results"].append(e["result"])
        branch_points.append({"from": src, "switch": sw, "site": site,
                              "n": len(tgt), "targets": tgt})

    by_type = collections.Counter(e["type"] for e in edges)
    main_next = {e["from"]: e["to"] for e in edges if e["type"] == "main"}
    outs, ins = collections.defaultdict(set), collections.defaultdict(set)
    for e in edges:
        outs[e["from"]].add(e["to"])
        ins[e["to"]].add(e["from"])
    known = set(nodes)
    unknown = collections.Counter(e["to"] for e in edges if e["to"] not in known)
    endings = collections.Counter(e["from"] for e in edges if e["type"] == "ending")

    json.dump({"built_for": "1.0.6001.0", "nodes": nodes, "edges": edges,
               "main_next": main_next, "branch_points": branch_points},
              open(os.path.join(BASE, "data", "scene_graph.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=0, sort_keys=True)

    con.execute("drop table if exists scene_edges")
    con.execute("""create table scene_edges(
        src text, dst text, type text, fn text, cond text, switch text, result text,
        site int, line int)""")
    con.executemany("insert into scene_edges values(?,?,?,?,?,?,?,?,?)",
                    [(e["from"], e["to"], e["type"], e["fn"], e["cond"], e["switch"],
                      e["result"], e["site"] or 0, e["line"]) for e in edges])
    con.commit()

    print("节点 %d ／ 边 %d ／ 分支点 %d" % (len(nodes), len(edges), len(branch_points)))
    print("边类型:", dict(by_type))
    print("有去向场景 %d ／ 无去向 %d ／ 有结局出口 %d" % (len(outs), len(nodes) - len(outs), len(endings)))
    print("未解析目标 top6:", unknown.most_common(6))
    print("\n分支点抽样（优先看有判定的）:")
    shown = 0
    for b in branch_points:
        if b["n"] < 2 or not b["switch"].startswith(("Ch_", "M", "S_")):
            continue
        print("  %s 判定=%s 行%s" % (b["from"], b["switch"], b["site"]))
        for t in b["targets"][:5]:
            print("     结果%s → %s（%s）%s" % ("/".join(t["results"]), t["to"], t["type"],
                                            nodes.get(t["to"], {}).get("title", "")))
        shown += 1
        if shown >= 4:
            break
    con.close()


main()
