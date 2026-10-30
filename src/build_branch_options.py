# -*- coding: utf-8 -*-
"""分支选项去向：精确条件 → 宽松条件 → 编号序列推定。"""
import io, json, os, re, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
cb = json.load(open(os.path.join(B, "choice_branch.json"), encoding="utf-8"))
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
titles = {r["script"]: (r["title"] or "") for r in c.execute("select script,title from scenes")}
allscenes = set(titles)
edges = {}
for r in c.execute("select src,dst,cond from scene_edges where cond<>''"):
    edges.setdefault(r["src"], []).append(((r["cond"] or ""), r["dst"]))

out, total, linked, by_num = {}, 0, 0, 0
for script, groups in cb.items():
    if not isinstance(groups, list):
        continue
    gs = []
    for gi, g in enumerate(groups):
        var = str(g.get("var") or "")
        opts = []
        for o in (g.get("options") or []):
            txt = (o.get("text") or "").strip()
            if not txt:
                continue
            idx = str(o.get("idx") or "")
            nxt = (o.get("next") or "").strip() or None
            how = "直连" if nxt else ""
            if not nxt and var:
                # 1) 精确：choice_var == idx
                for ec, ed in edges.get(script, []):
                    if ("choice_%s == %s" % (var, idx)) in ec or ("choice_%s==%s" % (var, idx)) in ec:
                        nxt, how = ed, "判定"
                        break
            if not nxt and var:
                # 2) 宽松：同场边里同时出现 var 与序号
                for ec, ed in edges.get(script, []):
                    if var in ec and re.search(r"==\s*%s\b" % re.escape(idx), ec):
                        nxt, how = ed, "判定"
                        break
            if not nxt and idx.isdigit():
                # 3) 编号序列：剧本常以 父_01 / 父_02 命名分岔场
                for cand in ("%s_%02d" % (script, int(idx)), "%s_%s" % (script, idx),
                             "%s_%02d_01" % (script, int(idx))):
                    if cand in allscenes:
                        nxt, how = cand, "编号推定"
                        break
            total += 1
            if nxt:
                linked += 1
                if how == "编号推定":
                    by_num += 1
            opts.append({"order": gi + 1, "idx": idx, "text": txt,
                         "cond": (o.get("cond") or "").strip(),
                         "effects": o.get("effects") or [], "next": nxt, "how": how})
        if opts:
            gs.append({"prompt": (g.get("prompt") or "").strip(), "options": opts})
    if gs:
        out[script] = {"title": titles.get(script, ""), "groups": gs}

json.dump(out, open(os.path.join(B, "branch_options.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("场景 %d｜选项 %d｜有去向 %d（%.0f%%），其中编号推定 %d"
      % (len(out), total, linked, 100.0 * linked / max(1, total), by_num))
