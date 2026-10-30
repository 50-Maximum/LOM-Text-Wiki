# -*- coding: utf-8 -*-
"""核验构建结果，并重新生成「待定地点清单」（带摘要、排除已定与回忆/梦境）。"""
import io, json, os, re, shutil, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
D = os.path.join(BASE, "data")
con = sqlite3.connect(os.path.join(D, "wiki.db"))
con.row_factory = sqlite3.Row

todo, note, ok = [], [], 0
for r in con.execute("select slug,type,sections from pages where type='场景'"):
    sc = r["slug"].split("/", 1)[1]
    h = ""
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息":
            h = s.get("html") or ""
    if "场景性质：" in h:
        note.append(sc)
    elif "地点：" in h:
        ok += 1
    else:
        todo.append(sc)
print("有地点", ok, "回忆/梦境", len(note), "待定", len(todo))

titles = {r["script"]: r["title"] for r in con.execute("select script,title from scenes")}
spk, rep = {}, {}
for r in con.execute("select script,seq,text,speaker from lines order by script,seq"):
    t = (r["text"] or "").replace("\n", " ").strip()
    sp = (r["speaker"] or "").strip()
    if sp and sp not in spk.setdefault(r["script"], []):
        spk[r["script"]].append(sp)
    if r["script"] not in rep and len(t) >= 10:
        rep[r["script"]] = t[:40]

todo.sort()
lines = []
n = 0
for sc in todo:
    n += 1
    parts = ["%03d %s" % (n, sc)]
    if titles.get(sc):
        parts.append(titles[sc])
    if spk.get(sc):
        parts.append("人物 " + "、".join(spk[sc][:3]))
    if rep.get(sc):
        parts.append('"%s"' % rep[sc])
    lines.append("　".join(parts))

p = os.path.join(D, "待定地点清单_带摘要.txt")
open(p, "w", encoding="utf-8").write("\n".join(lines))
shutil.copy(p, r"C:\Users\Luo\Desktop\待定地点清单_带摘要.txt")
print("新清单", len(todo), "条 →", p)
for L in lines[:8]:
    print("  ", L)
