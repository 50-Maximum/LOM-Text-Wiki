# -*- coding: utf-8 -*-
"""核验战斗行是否带关卡名。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(BASE + r"\data\wiki.db")
c.row_factory = sqlite3.Row
out = []
for sc in ["S0003_02_07", "S0017_01", "S0014_01_01"]:
    r = c.execute("select name,sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    out.append("\n== %s %s" % (sc, r["name"] if r else "无页"))
    if not r:
        continue
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "接下来":
            for x in (s.get("rows") or [])[:6]:
                out.append("   " + (x.get("note") or ""))
n = 0
for r in c.execute("select sections from pages where type='场景'"):
    for s in json.loads(r[0] or "[]"):
        if s.get("h") == "接下来":
            n += sum(1 for x in (s.get("rows") or []) if "战斗：" in (x.get("note") or ""))
            break
out.append("\n全站带名字的战斗行 %d 条" % n)
open(BASE + r"\data\_battle_name_check.txt", "w", encoding="utf-8").write("\n".join(out))
print("ok")
