# -*- coding: utf-8 -*-
import io, sqlite3, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("== 毛二壮 全部出现 ==")
for r in c.execute("select script,seq,speaker,text from lines where text like '%毛二壮%'"):
    print("  [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:90]))
print("\n== 白鲨帮 帮主 ==")
for r in c.execute("select script,seq,speaker,text from lines where text like '%白鲨帮%' and text like '%帮主%' limit 6"):
    print("  [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:90]))
print("\n== intros_char 里 毛二壮/王二壮 ==")
d = json.load(open(r"D:\LegendOfMortal Wiki\data\intros_char.json", encoding="utf-8"))
for k in d:
    if "毛二壮" in k or "王二壮" in k:
        print("  ", k, "→", json.dumps(d[k], ensure_ascii=False)[:200])
