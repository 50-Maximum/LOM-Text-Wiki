# -*- coding: utf-8 -*-
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
row = c.execute("select slug,type,facet,facet2 from pages where name like '%叶云裳初尝杀孽%'").fetchone()
print("页:", row)
sec = c.execute("select sections from pages where name like '%叶云裳初尝杀孽%'").fetchone()[0]
for s in json.loads(sec):
    print("  [%s] %d 行" % (s.get("h"), len(s.get("rows") or [])))
    for r in (s.get("rows") or [])[:5]:
        print("     -", (r.get("title") or r.get("note"))[:40], "|", r.get("slug") or r.get("script"))

# 该事件的笔记落在哪些剧本
names = [r[0] for r in c.execute("select name from pages where name like '%叶云裳初尝杀孽%'")]
print("\n对应笔记剧本：")
for nm in names:
    for r in c.execute("select script,seq_from,seq_to from notes where type='事件' and name=? limit 8", (nm,)):
        print("   ", r)

nxt = json.load(open(B + r"\scene_next.json", encoding="utf-8"))
seg = json.load(open(B + r"\story_segments.json", encoding="utf-8"))
segof = seg.get("seg_of") or {}
segmap = {s["id"]: s for s in seg.get("segments") or []}
print("\n剧本转场 / 所属段：")
for nm in names:
    for (sc,) in c.execute("select distinct script from notes where type='事件' and name=?", (nm,)):
        d = nxt.get(sc) or {}
        sid = segof.get(sc, "")
        sg = segmap.get(sid) or {}
        print("   %-24s next=%-16s edges=%d seg=%s route=%s next_seg=%s branches=%d"
              % (sc, d.get("next"), len(d.get("edges") or []), sid, sg.get("route"),
                 sg.get("next_seg"), len(sg.get("branches") or [])))
