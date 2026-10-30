# -*- coding: utf-8 -*-
"""地点质量排查：①place × 章节 交叉表 ②抽样看「崆峒山」事件是不是真在崆峒 ③空地点事件的样例"""
import io, sys, json, sqlite3, collections, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

print("=== 场景 place × chapter（只列 >=5 的格子）")
tab = collections.Counter()
for p, ch, n in c.execute("""select coalesce(place,''), coalesce(chapter,''), count(*)
                             from scenes group by 1,2"""):
    tab[(p, ch)] += n
places = sorted({p for p, _ in tab})
chs = ["序章", "外姓弟子", "南宫寿宴", "江陵围城", "唐门衰败", "比武招亲", "武林大会", "武林盟进攻唐门"]
print("  %-12s" % "", end="")
for ch in chs:
    print("%-9s" % ch[:8], end="")
print()
for p in places:
    if not any(tab[(p, ch)] >= 5 for ch in chs):
        continue
    print("  %-12s" % (p or "（空）"), end="")
    for ch in chs:
        v = tab[(p, ch)]
        print("%-9s" % (v or ""), end="")
    print()

print("\n=== 标了「崆峒山/崆峒」但章节是早期（序章/外姓弟子）的事件样例")
rows = c.execute("""select p.slug, json_extract(p.infobox,'$.发生地'), s.chapter
                    from pages p join scenes s on s.script = (
                        select script from scene_order limit 0)
                    where 0""").fetchall()
# 直接按场景查
susp = []
for slug, inf, secs in c.execute("select slug,infobox,sections from pages where type='事件'"):
    try:
        i = json.loads(inf or "{}")
        S = json.loads(secs or "[]")
    except Exception:
        continue
    place = (i.get("发生地") or "")
    ch = i.get("出现阶段") or ""
    scs = [r.get("script") for s in S if s.get("h") == "发生场景" for r in (s.get("rows") or [])]
    if not scs:
        continue
    reals = {c.execute("select place from scenes where script=?", (x,)).fetchone()[0] or "" for x in scs}
    if place.startswith("崆峒") and ("序章" in ch or "外姓弟子" in ch):
        susp.append((slug, place, ch, sorted(reals)))
print(" 可疑 %d 个，前 10：" % len(susp))
for x in susp[:10]:
    print("  ", x[0][:36], "|", x[1], "|", x[2], "|", x[3])

print("\n=== 空地点事件抽样（看正文里的地点线索）")
random.seed(7)
n = 0
for slug, inf, secs in c.execute("""select slug,infobox,sections from pages where type='事件'"""):
    i = json.loads(inf or "{}")
    if i.get("发生地"):
        continue
    S = json.loads(secs or "[]")
    scs = [r.get("script") for s in S if s.get("h") == "发生场景" for r in (s.get("rows") or [])]
    if not scs:
        continue
    if n >= 8:
        break
    n += 1
    print("\n ", slug)
    for sc in scs[:2]:
        title, place = c.execute("select title,coalesce(place,'') from scenes where script=?", (sc,)).fetchone()
        print("    场景 %-18s %-16s place=%s" % (sc, (title or "")[:14], place or "（空）"))
        for seq, sp, tx in c.execute("""select seq,speaker,text from lines where script=?
                                        and coalesce(branch,'')='' order by seq limit 3""", (sc,)):
            print("       %s：%s" % ((sp or "")[:8], (tx or "").replace("\n", " ")[:70]))
