# -*- coding: utf-8 -*-
"""核验：场景页里的选项是否已是真文案。"""
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
        if s.get("h") in ("分支选项", "分支与后果"):
            print("  [%s]" % s["h"])
            for x in (s.get("choices") or [])[:4]:
                opts = [o.get("text", "") for o in (x.get("options") or [])][:6]
                print("    ", x.get("kind"), opts)
            for x in (s.get("rows") or [])[:3]:
                print("    ", (x.get("note") or "")[:80])
print("\n全库占位选项:", c.execute(
    "select count(*) from branch_nodes where kind='choose' and (text like '选项%' or text='')").fetchone()[0])
