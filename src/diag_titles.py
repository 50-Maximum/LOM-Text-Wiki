# -*- coding: utf-8 -*-
"""无标题/泛标题场景按句数分布，判断能否用旁白自动起名。"""
import io, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row
GEN = {"结果", "这是因为", "你的领悟", "你的干劲", "你的决心", "你的勇气"}
rows = con.execute("select script,title,line_count,chapter from scenes").fetchall()
bad = [r for r in rows if not (r["title"] or "").strip() or (r["title"] or "") in GEN]
print("需命名:", len(bad))
b = collections.Counter()
for r in bad:
    n = r["line_count"] or 0
    b["1句" if n <= 1 else ("2-5句" if n <= 5 else ("6-20句" if n <= 20 else "20句以上"))] += 1
print(dict(b))
print("\n前 12 条:")
for r in bad[:12]:
    first = con.execute("select text,speaker from lines where script=? order by seq limit 1",
                        (r["script"],)).fetchone()
    print("   %-28s %-6s %2d句 %s" % (r["script"], (r["title"] or "-"), r["line_count"] or 0,
                                     ((first["text"] or "")[:52] if first else "")))
