# -*- coding: utf-8 -*-
"""地点证据强度盘点：脚本前缀（确定）/ 场景标题（可查）/ 只靠词频（弱），并抽检弱证据。"""
import io, sys, os, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(B, "data", "wiki.db")).cursor()

PREFIX = ("alchemy", "forge", "kitchen", "door", "backmountain", "study", "center",
          "room1", "room2", "mall", "downtown", "secret",
          "section_01_01", "section_01_02", "section_01_03", "section_01_04",
          "section_01_05", "section_01_06", "section_02_01", "section_02_02", "section_02_03")
INF = json.load(open(os.path.join(B, "data", "scene_place_infer.json"), encoding="utf-8"))

rows = list(c.execute("select script,coalesce(place,''),coalesce(title,'') from scenes"))
strong, title_ev, weak, empty = [], [], [], []
for sc, p, t in rows:
    if not p:
        empty.append(sc)
    elif any(sc.lower().startswith(k) for k in PREFIX):
        strong.append(sc)
    elif sc in INF:
        title_ev.append(sc)
    else:
        weak.append((sc, p, t))

print("有地点 %d：脚本前缀确定 %d｜标题可查 %d｜只靠词频 %d｜无地点 %d"
      % (len(rows) - len(empty), len(strong), len(title_ev), len(weak), len(empty)))
print("\n=== 弱证据抽样（词频猜的）")
for sc, p, t in weak[:12]:
    first = c.execute("""select text from lines where script=? order by seq limit 2""", (sc,)).fetchall()
    print("  %-20s %-14s %-16s | %s" % (sc, p, (t or "")[:14],
                                        " / ".join((x[0] or "").replace("\n", " ")[:34] for x in first)))
