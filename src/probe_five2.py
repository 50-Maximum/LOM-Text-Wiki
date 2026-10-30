# -*- coding: utf-8 -*-
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

print("== 王二壮 身份句 ==")
for r in c.execute("select script,seq,speaker,text from lines where text like '%王二壮%' and (text like '%帮主%' or text like '%畜生道%' or text like '%法王%' or text like '%丐帮%') limit 12"):
    print("  [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:90]))

print("\n== 畜生道法王 ==")
for r in c.execute("select script,seq,speaker,text from lines where text like '%畜生道法王%' limit 10"):
    print("  [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:90]))

print("\n== 铁拳掌门 / 飞天掌门 ==")
for kw in ["铁拳掌门", "飞天掌门"]:
    for r in c.execute("select script,seq,speaker,text from lines where text like ? limit 4", ("%" + kw + "%",)):
        print("  [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:90]))

print("\n== 吕翁 与 市井/商会 ==")
for r in c.execute("select script,seq,speaker,text from lines where text like '%吕翁%' limit 6"):
    print("  [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:90]))
