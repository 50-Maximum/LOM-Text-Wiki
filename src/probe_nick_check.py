# -*- coding: utf-8 -*-
"""复核几个可疑绰号/势力：老魔、龙王刀、锦香宫杀人魔、毛二壮与泥教。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for kw in ["老魔", "龙王刀", "锦香宫杀人魔"]:
    print("\n==", kw)
    for r in c.execute("select script,seq,speaker,text from lines where text like ? limit 4", ("%" + kw + "%",)):
        print("   [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:85]))

print("\n== 毛二壮 / 泥教 ==")
for r in c.execute("select script,seq,speaker,text from lines where text like '%毛二壮%' and text like '%泥教%' limit 4"):
    print("   [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:85]))
