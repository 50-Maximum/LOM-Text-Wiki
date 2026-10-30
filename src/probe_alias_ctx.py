# -*- coding: utf-8 -*-
import io, sys, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
names = [x.strip() for x in open(r"D:\LegendOfMortal Wiki\data\alias_candidates.txt",
                                encoding="utf-8") if x.strip()]
for nm in names:
    tot = c.execute("select count(*) from lines where text like ?", ("%" + nm + "%",)).fetchone()[0]
    rows = c.execute("""select script,seq,speaker,text from lines
                        where text like ? order by id limit 2""", ("%" + nm + "%",)).fetchall()
    print("\n### %s（%d 句）" % (nm, tot))
    for sc, sq, sp, tx in rows:
        m = re.search(r".{0,18}" + re.escape(nm) + r".{0,26}", tx)
        print("   [%s#%s %s] %s" % (sc, sq, sp or "-", (m.group(0) if m else tx)[:70]))
