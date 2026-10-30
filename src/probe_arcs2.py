# -*- coding: utf-8 -*-
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
arcs = json.load(open(os.path.join(B, "arcs.json"), encoding="utf-8"))
print("arcs 顺序:", arcs["arcs"])
print("\n-- 剧本所属章节/时间 --")
for sc in ["meeting_option_705_01", "S8400_01", "S8400_01_01", "ch0_5", "travel_result_401_501",
           "S9903_01", "ch8_1_1_2"]:
    r = c.execute("select script,chapter,title from scenes where script=?", (sc,)).fetchone()
    t = c.execute("select year,month,event from scene_time where script=?", (sc,)).fetchone()
    print("  %-24s 章=%-8s 题=%-20s 时=%s" %
          (sc, (r["chapter"] if r else "-"), (r["title"] if r else "-")[:20],
           (dict(t) if t else "-")))
print("\n-- guide_events 结构 --")
cols = [d[1] for d in c.execute("pragma table_info(guide_events)")]
print(cols)
for r in c.execute("select * from guide_events limit 2"):
    print({k: str(r[k])[:70] for k in r.keys()})
print("\n-- 段考约战 / 月度评鉴 的攻略条目 --")
for kw in ["段考", "月度评鉴", "万里鹏程"]:
    for r in c.execute("select * from guide_events where name like ?", ("%" + kw + "%",)):
        print("  ", {k: str(r[k])[:60] for k in r.keys()})
