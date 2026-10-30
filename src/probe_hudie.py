# -*- coding: utf-8 -*-
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("== 蝴蝶 相关全部 ==")
for r in c.execute("select script,seq,speaker,text from lines where text like '%蝴蝶%' limit 40"):
    t = (r["text"] or "").replace("\n", "／")
    print("  [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", t[:100]))
print("\n== S9905_01 全文（前后 30 句） ==")
for r in c.execute("select seq,speaker,text from lines where script='S9905_01' and seq<=60 order by seq limit 40"):
    t = (r["text"] or "").replace("\n", "／")
    print("  #%d %s：%s" % (r["seq"], r["speaker"] or "-", t[:100]))
