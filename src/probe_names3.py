# -*- coding: utf-8 -*-
"""取证：王公子/王二壮、辣手相公、裴红腊、胡壹千/胡离火、百万赵活、看诗集的道士。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
NAMES = ["王公子", "王二壮", "辣手相公", "裴红腊", "胡壹千", "胡离火", "百万赵活"]
for nm in NAMES:
    rows = list(c.execute("select script,seq,speaker,text from lines where text like ? limit 6",
                          ("%" + nm + "%",)))
    spk = [r[0] for r in c.execute("select distinct speaker from lines where speaker like ? limit 6", ("%" + nm + "%",))]
    print("\n== %-6s 命中 %d 句；说话人标记: %s" % (nm, len(rows), spk))
    for r in rows[:4]:
        print("   [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:90]))

print("\n== 诗集/文选 相关场景 ==")
for r in c.execute("select script,seq,speaker,text from lines where (text like '%诗集%' or text like '%文选%' or text like '%诗册%') limit 10"):
    print("   [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:80]))
