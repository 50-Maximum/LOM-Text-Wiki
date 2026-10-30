# -*- coding: utf-8 -*-
"""分支去向 v2：直接解析剧本 Lua 的 if choice_xxx == N then ... SetNextScript("Y")。"""
import io, json, os, re, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
RAW = os.path.join(B, "raw", "scripts")
cb = json.load(open(os.path.join(B, "choice_branch.json"), encoding="utf-8"))
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
titles = {r["script"]: (r["title"] or "") for r in c.execute("select script,title from scenes")}
allscenes = set(titles)

IF_RE = re.compile(r"if\s+choice_(\w+)\s*==\s*(\d+)\s*then")
TGT_RE = re.compile(r'(?:SetNextScript|SetCurrentStoryScript|SetCurrentTravelScript)\s*\(\s*"([^"]+)"\s*\)'
                    r'|ChangeScene\s*\(\s*"(\w+)"\s*,\s*"([^"]+)"\s*\)')


def parse_targets(script):
    p = os.path.join(RAW, script + ".txt")
    if not os.path.exists(p):
        return {}
    txt = open(p, encoding="utf-8", errors="replace").read().splitlines()
    out = {}
    cur = None
    for i, line in enumerate(txt):
        m = IF_RE.search(line)
        if m:
            cur = (m.group(1), int(m.group(2)))
            out.setdefault(cur, None)
            continue
        if cur is None:
            continue
        if re.match(r"\s*(elseif|else)\b", line):
            cur = None
            continue
        tm = TGT_RE.search(line)
        if tm:
            tgt = tm.group(1) or tm.group(3)
            if out.get(cur) is None:
                out[cur] = tgt
    return out


cache = {}
out, total, linked = {}, 0, 0
by = {"剧本": 0, "判定": 0, "编号": 0}
for script, groups in cb.items():
    if not isinstance(groups, list):
        continue
    if script not in cache:
        cache[script] = parse_targets(script)
    tg = cache[script]
    gs = []
    for gi, g in enumerate(groups):
        var = str(g.get("var") or "")
        opts = []
        for o in (g.get("options") or []):
            txt = (o.get("text") or "").strip()
            if not txt:
                continue
            idx = str(o.get("idx") or "")
            nxt, how = (o.get("next") or "").strip() or None, "剧本"
            if not nxt and idx.isdigit():
                key = (var, int(idx))
                if tg.get(key):
                    nxt, how = tg[key], "剧本"
            if not nxt:
                for cand in ("%s_%02d" % (script, int(idx)) if idx.isdigit() else "",):
                    if cand and cand in allscenes:
                        nxt, how = cand, "编号"
                        break
            total += 1
            if nxt:
                linked += 1
                by[how] = by.get(how, 0) + 1
            opts.append({"order": gi + 1, "idx": idx, "text": txt,
                         "cond": (o.get("cond") or "").strip(),
                         "effects": o.get("effects") or [], "next": nxt, "how": how if nxt else ""})
        if opts:
            gs.append({"prompt": (g.get("prompt") or "").strip(), "options": opts})
    if gs:
        out[script] = {"title": titles.get(script, ""), "groups": gs}

json.dump(out, open(os.path.join(B, "branch_options.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("场景 %d｜选项 %d｜有去向 %d（%.0f%%）｜来源 %s"
      % (len(out), total, linked, 100.0 * linked / max(1, total), by))
