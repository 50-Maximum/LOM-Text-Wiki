# -*- coding: utf-8 -*-
"""核验场景页「分支与后果」里的选项文案。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for sc in ["S0003_01_02", "S0208_04_break_start_01", "S0003_03_break_01"]:
    r = c.execute("select name,sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    print("\n==", sc, r["name"] if r else "无页")
    if not r:
        continue
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "分支与后果":
            for x in (s.get("choices") or [])[:8]:
                print("   %-7s #%s  %s" % (x.get("kind"), x.get("idx"), (x.get("text") or "")[:40]))
