# -*- coding: utf-8 -*-
"""统计有剧本但没场景页的情况（0 句/未建页），用于下一轮补页。"""
import io, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
pages = {r[0] for r in c.execute("select slug from pages where type='场景'")}
pages = {s[len("场景/"):] for s in pages}
rows = list(c.execute("select script,line_count,chapter,place,battles from scenes"))
missing = [r for r in rows if r["script"] not in pages]
lc = collections.Counter("0句" if (r["line_count"] or 0) <= 0 else "有台词" for r in missing)
print("scenes 总数 %d，场景页 %d，缺页 %d" % (len(rows), len(pages), len(missing)))
print("缺页情况:", dict(lc))
print("章节:", collections.Counter(r["chapter"] or "?" for r in missing).most_common(6))
print("有战斗标记的:", sum(1 for r in missing if (r["battles"] or "") not in ("", "0")))
for r in missing[:8]:
    print("   %-30s %3d句 %s" % (r["script"], r["line_count"] or 0, r["chapter"]))
