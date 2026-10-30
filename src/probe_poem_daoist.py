# -*- coding: utf-8 -*-
"""找「看诗集的道士」：青城相关场景里读书/读诗的道士。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("== 含「诗」且含「道士/道长」==")
n = 0
for r in c.execute("select script,seq,speaker,text from lines where text like '%诗%' and (text like '%道士%' or text like '%道长%') limit 20"):
    print("   [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:80]))
    n += 1
print("共", n)

print("\n== 说话人含「道长」且句子含「读/书/集」==")
for r in c.execute("select script,seq,speaker,text from lines where (speaker like '%道长%' or speaker like '%真人%' or speaker like '%子%') and (text like '%读%' or text like '%书%' or text like '%集%') limit 25"):
    print("   [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:80]))
