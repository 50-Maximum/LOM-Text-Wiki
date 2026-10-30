# -*- coding: utf-8 -*-
"""把每条 2~4 分命中的「具体是哪几条选项文案对上了」打出来，判断是不是泛化词撞车。"""
import io, sys, json, re, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
ref = json.load(open(B + r"\scene_time_ref.json", encoding="utf-8"))
tl = json.load(open(B + r"\ref_wiki\timeline.json", encoding="utf-8"))
titles = dict(c.execute("select script,title from scenes"))

cho = list(c.execute("select script,seq,options from choices"))
txt = list(c.execute("select script,seq,text from lines"))

def quotes(ev):
    out = []
    for m in re.findall(r"「([^」]{2,26})」", ev):
        s = re.sub(r"^[（(].*?[）)]", "", m.strip()).strip()
        if s and s not in out:
            out.append(s)
    return out

rows = {r["event"]: r for r in tl}
for sc, v in sorted(ref.items(), key=lambda x: x[1].get("score") or 0):
    s = v.get("score") or 0
    if s < 2 or s > 4:
        continue
    name = v.get("name") or ""
    cand = [ev for ev in rows if name and all(p in ev for p in name.split("／"))]
    if not cand:
        print("%-26s ｜ %s ｜ 找不到年表原行" % (sc, name))
        continue
    qs = quotes(cand[0])
    hit = []
    for q in qs:
        got = any(sc == r[0] and r[2] and q in r[2] for r in cho) or \
              any(sc == r[0] and q in (r[2] or "") for r in txt)
        if got:
            hit.append(q)
    print("%-26s %-16s 命中 %d/%d: %s"
          % (sc, name, len(hit), len(qs), "／".join(hit)))
    print("      场景: %s" % (titles.get(sc) or "-"))
