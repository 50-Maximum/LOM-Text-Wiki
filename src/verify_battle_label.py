# -*- coding: utf-8 -*-
"""核验战斗胜负标签是否出现在「接下来」栏。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
out = []
for sc in ["S0014_01_02", "S0020_02_03_01", "S0021_02_03", "act2_3"]:
    r = c.execute("select name,sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    if not r:
        out.append("%s 无页" % sc)
        continue
    out.append("\n== %s %s" % (sc, r["name"]))
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "接下来":
            for x in (s.get("rows") or [])[:8]:
                out.append("   " + (x.get("note") or ""))
n = sum(1 for r in c.execute("select sections from pages where type='场景'")
        for s in json.loads(r[0] or "[]") if s.get("h") == "接下来"
        for x in (s.get("rows") or []) if (x.get("note") or "").startswith("战斗胜利"))
m = sum(1 for r in c.execute("select sections from pages where type='场景'")
        for s in json.loads(r[0] or "[]") if s.get("h") == "接下来"
        for x in (s.get("rows") or []) if (x.get("note") or "").startswith("战斗失败"))
out.append("\n全站：战斗胜利标签 %d 条，战斗失败标签 %d 条" % (n, m))
open(r"D:\LegendOfMortal Wiki\data\_battle_check.txt", "w", encoding="utf-8").write("\n".join(out))
print("ok")
