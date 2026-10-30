# -*- coding: utf-8 -*-
"""待定地点清单（带摘要版）：编号 脚本号 标题｜出场人物｜代表台词。"""
import io, json, os, shutil, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
con.row_factory = sqlite3.Row
scenes = {r["script"]: dict(r) for r in con.execute(
    "select script,chapter,title,line_count from scenes")}

# 待定场次：有场景页但没有地点
todo = []
for r in con.execute("select slug,sections from pages where type='场景'"):
    sc = r["slug"].split("/", 1)[1]
    txt = ""
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息" and s.get("html"):
            txt = s["html"]
    if "地点：" in txt:
        continue
    todo.append(sc)
todo.sort()

# 台词：说话人 + 代表句
spk = {}
rep = {}
for r in con.execute("select script,seq,text,speaker from lines order by script,seq"):
    sc = r["script"]
    if sc not in scenes:
        continue
    t = (r["text"] or "").replace("\n", " ").strip()
    sp = (r["speaker"] or "").strip()
    if sp and sp not in spk.setdefault(sc, []):
        spk[sc].append(sp)
    if sc not in rep and len(t) >= 10 and sp and sp not in ("旁白", "我"):
        rep[sc] = (sp, t[:40])
    if sc not in rep and len(t) >= 10:
        rep[sc] = (sp or "旁白", t[:40])

lines = []
n = 0
for sc in todo:
    n += 1
    d = scenes.get(sc, {})
    title = d.get("title") or ""
    people = "、".join(spk.get(sc, [])[:3])
    q = rep.get(sc)
    parts = ["%03d %s" % (n, sc)]
    if title:
        parts.append(title)
    if people:
        parts.append("人物 " + people)
    if q:
        parts.append('"%s"' % q[1])
    lines.append("　".join(parts))

p = os.path.join(BASE, "data", "待定地点清单_带摘要.txt")
open(p, "w", encoding="utf-8").write("\n".join(lines))
shutil.copy(p, r"C:\Users\Luo\Desktop\待定地点清单_带摘要.txt")
print("共", len(todo), "条 →", p)
for L in lines[20:40]:
    print(L)
