# -*- coding: utf-8 -*-
import io, sys, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for nm in ("虞小梅", "夏侯兰", "魏菊"):
    print("\n### %s 与门禁同句" % nm)
    for r in c.execute("""select script,seq,speaker,text from lines
                          where text like ? and (text like '%弟子%' or text like '%门人%'
                                or text like '%门下%' or text like '%四姝%')
                          limit 6""", ("%" + nm + "%",)):
        print("   [%s#%s %s] %s" % (r[0], r[1], r[2], r[3][:100].replace("\n", " ")))
