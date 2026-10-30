# -*- coding: utf-8 -*-
"""审事件页的「发生地」：与所属场景的 place 是否一致、有没有空值/怪值。"""
import io, sys, json, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

# 场景 place 分布
print("=== 场景 place 取值（前 20）")
for p, n in c.execute("""select coalesce(place,''), count(*) from scenes
                         group by 1 order by 2 desc limit 20"""):
    print("  %-16s %d" % (repr(p), n))

print("\n=== 事件页 发生地 分布")
for p, n in c.execute("""select json_extract(infobox,'$.发生地'), count(*) from pages
                         where type='事件' group by 1 order by 2 desc limit 20"""):
    print("  %-24s %d" % (repr(p), n))

print("\n=== 事件页：发生地 与 场景 place 不一致的例子")
bad = []
for slug, inf, secs in c.execute("""select slug,infobox,sections from pages where type='事件'"""):
    try:
        i = json.loads(inf or "{}")
        S = json.loads(secs or "[]")
    except Exception:
        continue
    ev_places = (i.get("发生地") or "").strip()
    scs = []
    for s in S:
        if s.get("h") == "发生场景":
            for r in s.get("rows") or []:
                if r.get("script"):
                    scs.append(r["script"])
    if not scs:
        continue
    real = []
    for sc in scs:
        row = c.execute("select place from scenes where script=?", (sc,)).fetchone()
        p = (row[0] if row else "") or ""
        if p and p not in real:
            real.append(p)
    real_s = "、".join(real)
    if ev_places != real_s:
        bad.append((slug, ev_places, real_s, scs))
print(" 不一致 %d 个，前 15：" % len(bad))
for slug, a, b, scs in bad[:15]:
    print("  %-34s 页面[%s] 场景[%s] %s" % (slug[:34], a or "空", b or "空", scs[:2]))

print("\n=== 事件页 发生地 为空的数量")
n0 = c.execute("""select count(*) from pages where type='事件'
                  and (json_extract(infobox,'$.发生地') is null
                       or json_extract(infobox,'$.发生地')='')""").fetchone()[0]
print(" ", n0)
