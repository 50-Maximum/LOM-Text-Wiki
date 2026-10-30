# -*- coding: utf-8 -*-
"""抽查链式推断（承前场/接续场）的场次，看正文是否与判定地点相符。"""
import io, json, random, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

samples = []
for r in c.execute("select slug, sections from pages where type='场景'"):
    txt = ""
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息" and s.get("html"):
            txt = s["html"]
    if "地点：" not in txt:
        continue
    body = txt.split("地点：", 1)[1]
    pl = body.split("（依据：", 1)[0].strip()
    ev = body.split("（依据：", 1)[1].rsplit("）", 1)[0] if "（依据：" in body else ""
    if ev.startswith(("接续场", "承前场")):
        samples.append((r["slug"].replace("场景/", ""), pl, ev))

random.seed(3)
print("链式推断合计:", len(samples))
for sc, pl, ev in random.sample(samples, min(6, len(samples))):
    d = c.execute("select title from scenes where script=?", (sc,)).fetchone()
    print("\n== %s | %s | %s → %s" % (sc, (d["title"] if d else "") or "", ev, pl))
    n = 0
    for r in c.execute("select seq, text from lines where script=? order by seq", (sc,)):
        t = (r["text"] or "").replace("\n", " ")
        if len(t) > 12:
            print("   #%d %s" % (r["seq"], t[:70]))
            n += 1
            if n >= 2:
                break
