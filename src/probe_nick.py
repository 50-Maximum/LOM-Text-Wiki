# -*- coding: utf-8 -*-
"""取证：龙湘的三个绰号、点苍双尊是哪两人、点苍剑圣出现在哪些事。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

print("== 点苍双尊 ==")
for r in c.execute("select script,seq,speaker,text from lines where text like '%双尊%' limit 8"):
    print("   [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:90]))

print("\n== 点苍剑圣 / 剑圣 ==")
for r in c.execute("select script,seq,speaker,text from lines where text like '%点苍剑圣%' limit 8"):
    print("   [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:90]))

print("\n== 龙湘 相关（号/人称/侠/仙子）==")
for r in c.execute("""select script,seq,speaker,text from lines where text like '%龙湘%'
                      and (text like '%号%' or text like '%人称%' or text like '%绰号%' or text like '%外号%'
                           or text like '%仙%' or text like '%侠%') limit 12"""):
    print("   [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:90]))
