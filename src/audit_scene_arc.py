# -*- coding: utf-8 -*-
"""按章节核对场景阶段：章=第N章，但阶段不等于该章应有的阶段 → 可疑。"""
import io, json, os, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
arcs = json.load(open(os.path.join(B, "arcs.json"), encoding="utf-8"))
chmap = arcs["chapter_map"]
sc = {r["script"]: r["chapter"] for r in c.execute("select script,chapter from scenes")}
facet = {}
for r in c.execute("select sort_key,facet from pages where type='场景'"):
    facet[r["sort_key"]] = r["facet"]
bad = collections.defaultdict(list)
for s, f in facet.items():
    ch = sc.get(s) or ""
    want = chmap.get(ch)
    if want and f != want:
        bad[(ch, f)].append(s)
print("场景页 %d，章节与阶段不符 %d 处" % (len(facet), sum(len(v) for v in bad.values())))
for (ch, f), lst in sorted(bad.items(), key=lambda x: -len(x[1]))[:15]:
    print("   %-8s 应为 %-10s 实为 %-10s  %d 场  例：%s"
          % (ch, chmap.get(ch, ""), f, len(lst), lst[0]))
json.dump({f"{k[0]}|{k[1]}": v for k, v in bad.items()},
          open(os.path.join(B, "research", "arc_mismatch.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("明细写入 data\\research\\arc_mismatch.json")
