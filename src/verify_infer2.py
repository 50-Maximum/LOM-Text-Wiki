# -*- coding: utf-8 -*-
"""覆盖率统计（修正括号解析）+ 抽查编号推断场次的正文是否对得上。"""
import io, json, random, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

by_ev = collections.Counter()
samples = []
for r in c.execute("select slug, sections from pages where type='场景'"):
    txt = ""
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息" and s.get("html"):
            txt = s["html"]
    if "地点：" not in txt:
        by_ev["（无地点）"] += 1
        continue
    body = txt.split("地点：", 1)[1]
    pl = body.split("（依据：", 1)[0].strip()
    ev = body.split("（依据：", 1)[1].rsplit("）", 1)[0] if "（依据：" in body else ""
    by_ev[ev] += 1
    if ev.startswith("编号规律"):
        samples.append((r["slug"], pl))

print("按依据统计:")
for k, v in by_ev.most_common():
    print("   %-16s %d" % (k, v))

print("\n抽查 6 场（编号推断）:")
random.seed(11)
for slug, pl in random.sample(samples, min(6, len(samples))):
    sc = slug.replace("场景/", "")
    d = c.execute("select title from pages where slug=?", (slug,)).fetchone()
    print("\n== %s | %s | 判为 %s" % (sc, d["title"] if d else "", pl))
    n = 0
    for r in c.execute("select seq,speaker,text from lines where script=? order by seq", (sc,)):
        t = (r["text"] or "").replace("\n", " ")
        if any(k in t for k in ("唐门", "崆峒", "江陵", "襄阳", "眉山", "锦香", "青城", "点苍")):
            print("   #%d %s %s" % (r["seq"], (r["speaker"] or "")[:6], t[:80]))
            n += 1
            if n >= 2:
                break
