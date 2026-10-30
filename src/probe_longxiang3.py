# -*- coding: utf-8 -*-
"""列卧云岗相关场景的选项组，找龙湘三个绰号。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
scs = [r[0] for r in c.execute("select script from scenes where place like '%卧云岗%'")]
print("卧云岗场景", len(scs))
for sc in scs:
    for r in c.execute("select seq,checkpoint,options from choices where script=?", (sc,)):
        opts = json.loads(r["options"] or "[]")
        txts = [o.get("text", "") for o in opts]
        if any("龙" in t or "侠" in t or "仙" in t for t in txts):
            print("\n[%s#%d] %s" % (sc, r["seq"], r["checkpoint"]))
            for o in opts:
                print("   -", o.get("text", "")[:40], "| cond", o.get("cond", "")[:20])
