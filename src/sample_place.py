# -*- coding: utf-8 -*-
"""抽样看事件页的地点对不对：打印事件名、页面地点、场景、场景里前几句。"""
import io, sys, json, sqlite3, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

def show(slug, inf, secs):
    i = json.loads(inf or "{}")
    S = json.loads(secs or "[]")
    scs = [r.get("script") for s in S if s.get("h") == "发生场景" for r in (s.get("rows") or [])]
    print("  %-30s 地点=%s" % (slug[3:33], i.get("发生地") or "（空）"))
    for sc in scs[:2]:
        t, p = c.execute("select title,coalesce(place,'') from scenes where script=?", (sc,)).fetchone()
        print("     场 %-20s %-16s place=%s" % (sc, (t or "")[:14], p or "空"))
        for seq, sp, tx in c.execute("""select seq,speaker,text from lines where script=?
                                        order by seq limit 2""", (sc,)):
            print("        %-8s %s" % ((sp or "")[:8], (tx or "").replace("\n", " ")[:64]))

rows = list(c.execute("select slug,infobox,sections from pages where type='事件'"))
print("事件页 %d" % len(rows))

print("\n=== A. 地点写「崆峒山」的抽样")
n = 0
for slug, inf, secs in rows:
    if '崆峒山' in (inf or "") and n < 5:
        show(slug, inf, secs); n += 1

print("\n=== B. 地点为空的抽样")
n = 0
for slug, inf, secs in rows:
    if '"发生地"' not in (inf or "") and n < 6:
        show(slug, inf, secs); n += 1

print("\n=== C. 地点写「唐门」但场景标题含崆峒/锦香宫的抽样")
n = 0
for slug, inf, secs in rows:
    if n >= 5:
        break
    i = json.loads(inf or "{}")
    if i.get("发生地") not in ("唐门", None):
        continue
    S = json.loads(secs or "[]")
    scs = [r.get("script") for s in S if s.get("h") == "发生场景" for r in (s.get("rows") or [])]
    for sc in scs:
        t = c.execute("select title from scenes where script=?", (sc,)).fetchone()[0] or ""
        if "崆峒" in t or "锦香宫" in t:
            show(slug, inf, secs); n += 1
            break
