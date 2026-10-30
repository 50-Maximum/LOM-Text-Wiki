# -*- coding: utf-8 -*-
"""找卧云岗事件里给龙湘的称号选项。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
rows = list(c.execute("select script,seq,checkpoint,options from choices"))
print("选项组", len(rows))
hit = 0
for r in rows:
    opts = r["options"] or ""
    if any(k in opts for k in ("女侠", "仙子", "侠女", "剑仙", "魔女", "仙子")):
        n = c.execute("select text from lines where script=? limit 3", (r["script"],)).fetchall()
        ctx = " / ".join((x[0] or "")[:20] for x in n)
        print("\n[%s#%d] %s" % (r["script"], r["seq"], r["checkpoint"]))
        print("   选项:", opts[:160])
        print("   前后:", ctx[:80])
        hit += 1
        if hit >= 8:
            break
print("\n命中", hit)
