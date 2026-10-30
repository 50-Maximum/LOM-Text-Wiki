# -*- coding: utf-8 -*-
"""抽查事件链顺延的场次 + 复核之前判错的襄阳那场。"""
import io, json, random, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row


def place_of_page(sc):
    r = c.execute("select sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    if not r:
        return None, None
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息" and s.get("html"):
            txt = s["html"]
            if "地点：" in txt:
                body = txt.split("地点：", 1)[1]
                return body.split("（依据：", 1)[0].strip(), \
                    (body.split("（依据：", 1)[1].rsplit("）", 1)[0] if "（依据：" in body else "")
    return None, None


print("复核 S2321_04_03_02_001（与小梅同游襄阳城）:",
      place_of_page("S2321_04_03_02_001"))

samples = []
for r in c.execute("select slug from pages where type='场景'"):
    sc = r["slug"].replace("场景/", "")
    pl, ev = place_of_page(sc)
    if ev and ev.startswith("事件链顺延"):
        samples.append((sc, pl, ev))
print("事件链顺延合计:", len(samples))
random.seed(5)
for sc, pl, ev in random.sample(samples, min(5, len(samples))):
    d = c.execute("select title from scenes where script=?", (sc,)).fetchone()
    print("\n== %s | %s → %s" % (sc, (d["title"] if d else "") or "", pl))
    n = 0
    for r in c.execute("select seq,text from lines where script=? order by seq", (sc,)):
        t = (r["text"] or "").replace("\n", " ")
        if len(t) > 14:
            print("   #%d %s" % (r["seq"], t[:70]))
            n += 1
            if n >= 2:
                break
