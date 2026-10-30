# -*- coding: utf-8 -*-
"""整理每条路线的证据包：入口、互斥、被门禁的场景、旗标语义。

读 routes_raw.json + flags + branch_nodes + scenes + flaginfo
写 data/routes_dossier.json
"""
import os, sys, io, json, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))

raw = json.load(open(os.path.join(BASE, "data", "routes_raw.json"), encoding="utf-8"))
labels = {f: l for f, l in c.execute("select flag,label from flaginfo")}
scenes = {r[0]: {"title": r[1], "chapter": r[2], "lines": r[3]}
          for r in c.execute("select script,title,chapter,line_count from scenes")}

# 每个抉择点各臂设置了哪些旗标
point_flags = collections.defaultdict(lambda: collections.defaultdict(list))
for r in c.execute("""select script,seq,text,flags from branch_nodes
                      where flags<>'[]' and kind in ('dice','choose')"""):
    script, seq, text, fl = r
    for it in json.loads(fl):
        point_flags[(script, seq)][it["f"]].append({"v": it["v"], "opt": text})

# 同一抉择点里出现的路线旗标 → 互斥
GFLAGS = set(labels) & set(raw)
exclusive_of = collections.defaultdict(set)
for (script, seq), m in point_flags.items():
    flags_here = [f for f in m if f in GFLAGS]
    for f in flags_here:
        for g in flags_here:
            if g != f:
                exclusive_of[f].add(g)

dossier = {}
for fid, pack in raw.items():
    sets = []
    for r in c.execute("""select script,seq,value,branch from flags
                          where flag=? order by script,seq""", (fid,)):
        sc, sq, v, br = r
        # 该设置点前后有没有选项
        opts = [{"idx": x[0], "text": x[1], "cond": x[2]}
                for x in c.execute("""select idx,text,cond from branch_nodes
                                      where script=? and seq=? and kind in ('dice','choose')
                                      order by idx""", (sc, sq))]
        sets.append({"script": sc, "title": scenes.get(sc, {}).get("title", ""),
                     "chapter": scenes.get(sc, {}).get("chapter", ""),
                     "seq": sq, "value": v, "ctx": br[:120], "options": opts})

    gated = []
    for x in pack["requires"]:
        sc = x["script"]
        gated.append({"script": sc, "title": scenes.get(sc, {}).get("title", ""),
                      "chapter": scenes.get(sc, {}).get("chapter", ""),
                      "lines": scenes.get(sc, {}).get("lines", 0)})

    dossier[fid] = {
        "flag": fid,
        "label": labels.get(fid, pack.get("name", "")),
        "name": pack.get("name", ""),
        "set_points": sets,
        "gated_count": len(gated),
        "gated": gated,
        "exclusive": sorted(exclusive_of.get(fid, [])),
    }

out = os.path.join(BASE, "data", "routes_dossier.json")
json.dump(dossier, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("路线", len(dossier))
for f, d in dossier.items():
    print(f"  {f} {d['label']}｜设置点 {len(d['set_points'])}｜门禁场景 {d['gated_count']}｜互斥 {d['exclusive']}")
