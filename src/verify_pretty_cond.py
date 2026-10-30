# -*- coding: utf-8 -*-
"""核验条件链是否已展开成人话。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for sc in ["ch6_7_1", "ch5_4_7_1"]:
    r = c.execute("select name,sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    print("\n==", sc, r["name"] if r else "无页")
    if not r:
        continue
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "分支与后果":
            for x in (s.get("choices") or [])[:4]:
                cd = x.get("cond") or ""
                if cd:
                    print("   %s | %s" % ((x.get("text") or "")[:18], cd[:110]))
