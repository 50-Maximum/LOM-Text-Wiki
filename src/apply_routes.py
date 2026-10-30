# -*- coding: utf-8 -*-
"""把 routes_authored.json 连同自动证据写进 routes 表。

证据 = 该路线旗标门禁的场景清单（按台词数取前 12）+ 设置点。
"""
import os, sys, io, json, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.execute("PRAGMA journal_mode=WAL")

authored = json.load(open(os.path.join(BASE, "data", "routes_authored.json"), encoding="utf-8"))
raw = json.load(open(os.path.join(BASE, "data", "routes_raw.json"), encoding="utf-8"))
labels = {f: l for f, l in c.execute("select flag,label from flaginfo")}
scenes = {r[0]: {"title": r[1], "chapter": r[2], "lines": r[3]}
          for r in c.execute("select script,title,chapter,line_count from scenes")}

c.executescript("""drop table if exists routes;
create table routes(id INTEGER PRIMARY KEY, key TEXT, kind TEXT, flag TEXT, value INT,
                    summary TEXT, entry TEXT, beats TEXT, fates TEXT,
                    gated_count INT, gated TEXT, set_points TEXT);""")

def gated_for(flag, limit=14):
    pack = raw.get(flag)
    if not pack:
        return [], 0
    items = sorted(pack["requires"], key=lambda x: -(x.get("lines") or 0))
    out = [{"script": x["script"], "title": x["title"], "chapter": x["chapter"],
            "lines": x.get("lines")} for x in items[:limit]]
    return out, len(pack["requires"])

def set_points_for(flag, value=None):
    out = []
    for sc, sq, v, br in c.execute("""select script,seq,value,branch from flags
                                      where flag=? order by script,seq""", (flag,)):
        if value is not None and str(v) != str(value):
            continue
        out.append({"script": sc, "seq": sq, "value": v,
                    "title": scenes.get(sc, {}).get("title", "")})
    return out

n = 0
for r in authored["romance"]:
    flag = r["flag"]
    gated, cnt = gated_for(flag) if flag else ([], 0)
    sets = set_points_for(flag) if flag else []
    c.execute("""insert into routes(key,kind,flag,value,summary,entry,beats,fates,
                                    gated_count,gated,set_points)
                 values(?,?,?,?,?,?,?,?,?,?,?)""",
              (r["key"], "感情线", flag, r["lover"], r["summary"], r["entry"],
               json.dumps(r["beats"], ensure_ascii=False),
               json.dumps(r["fates"], ensure_ascii=False),
               cnt, json.dumps(gated, ensure_ascii=False), json.dumps(sets, ensure_ascii=False)))
    n += 1

for r in authored["branches"]:
    flag = r["flag"]
    val = r.get("value")
    gated, cnt = gated_for(flag)
    sets = set_points_for(flag, val)
    c.execute("""insert into routes(key,kind,flag,value,summary,entry,beats,fates,
                                    gated_count,gated,set_points)
                 values(?,?,?,?,?,?,?,?,?,?,?)""",
              (r["key"], "主线分支", flag, val, r["summary"], r["entry"],
               json.dumps(r["beats"], ensure_ascii=False),
               json.dumps(r["fates"], ensure_ascii=False),
               cnt, json.dumps(gated, ensure_ascii=False), json.dumps(sets, ensure_ascii=False)))
    n += 1

c.commit()
print("写入路线", n)
for row in c.execute("select id,key,kind,flag,value,gated_count from routes"):
    print("  ", row)
