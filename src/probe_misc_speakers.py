# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for sp in ("爹", "娘", "回音", "绝世高手", "轿中人", "蛇"):
    print("\n### 说话人", sp)
    for r in c.execute("select script,seq,speaker,text from lines where speaker=? limit 3", (sp,)):
        print("   [%s#%s] %s" % (r[0], r[1], r[3][:80].replace("\n", " ")))
