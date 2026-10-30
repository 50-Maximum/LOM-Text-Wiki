# -*- coding: utf-8 -*-
"""取证：四组同姓候选是否同一人（看称谓与事件）。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
PAIRS = [("申屠道长", "申屠师叔"), ("余公子", "余自咏"), ("翟长老", "翟老汉"), ("毛帮主", "毛二壮")]
for a, b in PAIRS:
    print("\n==========", a, "vs", b)
    for nm in (a, b):
        rows = list(c.execute("select script,seq,speaker,text from lines where text like ? limit 3",
                              ("%" + nm + "%",)))
        print("  --", nm, "命中", len(rows))
        for r in rows:
            print("     [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:70]))
