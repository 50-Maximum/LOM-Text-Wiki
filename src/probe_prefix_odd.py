# -*- coding: utf-8 -*-
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
q = ("select name from pages where type='人物' and (name like '华山派%' or name like '孤云山派%'"
     " or name like '巫灵教%' or name like '嵩山寺%' or name like '崆峒·%' or name like '岭南派%')")
for r in c.execute(q):
    print("  ", r["name"])
print("-- 华山派原句 --")
for r in c.execute("select script,seq,speaker,text from lines where text like '%华山派%' limit 5"):
    print("   [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:80]))
