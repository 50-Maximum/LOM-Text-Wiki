# -*- coding: utf-8 -*-
"""看 scene_edges 里战斗相关边是否已带 switch/result，决定要不要重解析。"""
import io, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
rows = list(c.execute("select src,dst,type,switch,result,cond from scene_edges where switch like '%Combat%' or switch like '%Battle%'"))
print("战斗结果边", len(rows))
for r in rows[:10]:
    print("   %-26s → %-26s type=%-7s sw=%-18s res=%s cond=%s" % (
        r["src"], r["dst"], r["type"], r["switch"], r["result"], (r["cond"] or "")[:20]))
print("\nswitch 取值分布:", collections.Counter(r["switch"] for r in rows).most_common(8))
print("type 分布:", collections.Counter(r["type"] for r in rows).most_common())
print("\n全部边的 type:", collections.Counter(r[0] for r in c.execute("select type from scene_edges")).most_common())
