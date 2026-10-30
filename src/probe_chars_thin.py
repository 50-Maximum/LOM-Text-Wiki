# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
rows = c.execute("select name,lead,mentions from pages where slug like '人物/%'").fetchall()
thin = [(n, l or "", m or 0) for n, l, m in rows if len(l or "") < 30]
print("人物页", len(rows), " 导语过短", len(thin))
for n, l, m in thin[:25]:
    print("   %-10s 提及%-4s %s" % (n, m, l[:50]))
